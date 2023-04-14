from __future__ import absolute_import, unicode_literals

# Django imports
from django.core.cache import cache
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.template.defaultfilters import slugify


# Python imports
from datetime import timedelta
import json
import requests
from html import unescape
from time import sleep
from requests import post as request_post
from requests import get as request_get
from base64 import b64encode
from os import environ
from boto3 import client
from re import sub as re_sub

# Local imports
from apps.logic.services import (
    bulk_create_articles_and_notifications,
    notifications_create,
    create_articles_from_feed,
    source_profile_img_create,
    twitter_create_api_settings,
    tweet_type_create,
)
from apps.article.models import Article, TweetType
from apps.home.models import NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source
from apps.scrapper.web_crawler import (
    crawl_thegeneralist,
    crawl_ben_evans,
    crawl_meritechcapital,
    crawl_stockmarketnerd,
)
from apps.scrapper.filler_words import full_fillerwords, short_fillerwords

# temporary imports
from django.contrib.auth import get_user_model
from apps.list.models import List
from apps.stock.models import Portfolio, Stock
from apps.source.models import SourceRating

User = get_user_model()


s3 = client("s3")


class SpotifyAPI(object):
    access_token = None
    access_token_expires = timezone.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credientals(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credientals()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        r = request_post(
            self.token_url, data=self.get_token_data(), headers=self.get_token_headers()
        )
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        data = r.json()
        expires_in = data["expires_in"]
        expires = timezone.now() + timedelta(seconds=expires_in)
        self.access_token = data["access_token"]
        self.access_token_expires = expires
        self.access_token_did_expire = expires < timezone.now()
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        if expires < timezone.now():
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_episodes(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        r = request_get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_podcaster(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        r = request_get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()


@shared_task
def scrape_twitter():
    api = twitter_create_api_settings()
    last_id = cache.get("last_id")
    if last_id:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", since_id=last_id, include_entities=True
        )
    else:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", include_entities=True
        )
    existing_tweets = Article.objects.filter(external_id__isnull=False).values_list(
        "external_id", flat=True
    )
    sources = Source.objects.all().only("source_id", "external_id")
    tweet_creation_list = []
    for status in statuses:
        try:
            tweet_external_id = status.id
            if str(tweet_external_id) not in existing_tweets:
                twitter_user_id = status.user.id
                if sources.filter(external_id=twitter_user_id).exists():
                    title = re_sub(r"http\S+", "", unescape(status.full_text))
                    if not title.strip():
                        continue
                    link = f"https://twitter.com/{status.user.screen_name}/status/{tweet_external_id}"
                    pub_date = status.created_at
                    # title, tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_creation_list.append(
                        {
                            "source": twitter_user_id,
                            "title": title,
                            "link": link,
                            "pub_date": pub_date,
                            "external_id": tweet_external_id,
                            "tweet_type": tweet_type,
                        }
                    )
            else:
                break
            last_id = tweet_external_id
        except:
            continue
    cache.set("last_id", last_id)
    new_articles = [
        Article(
            title=new_tweet["title"],
            link=new_tweet["link"],
            pub_date=new_tweet["pub_date"],
            source=sources.get(external_id=new_tweet["source"]),
            external_id=new_tweet["external_id"],
            tweet_type=new_tweet["tweet_type"],
        )
        for new_tweet in tweet_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Substack")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=substack_sources).only(
        "title", "pub_date", "source"
    )
    for source in substack_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles, True)
        sleep(30)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="SeekingAlpha")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=seekingalpha_sources).only(
        "title", "pub_date", "source"
    )
    for source in seekingalpha_sources:
        feed_url = f"{source.url}.xml"
        create_articles_from_feed(source, feed_url, articles)
        sleep(30)


@shared_task
def scrape_other_websites():
    other_sources = (
        Source.objects.filter(website=get_object_or_404(Website, name="Other"))
        .exclude(external_id__isnull=False)
        .only("source_id", "url", "website")
    )
    articles = Article.objects.filter(source__in=other_sources).only(
        "title", "pub_date", "source"
    )
    for source in other_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def scrape_news():
    news_sources = Source.objects.filter(news=True).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=news_sources).only(
        "title", "pub_date", "source"
    )
    for source in news_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def crawl_websites():
    crawl_sources = (
        Source.objects.filter(name="The Generalist")
        .filter(name="Benedict Evans")
        .filter(name="Meritech Capital")
        .filter(name="Stock Market Nerd")
        .filter(name="Palladium")
    )
    articles = Article.objects.filter(source__in=crawl_sources).only(
        "title", "pub_date", "source"
    )
    crawl_thegeneralist(articles)
    crawl_ben_evans(articles)
    crawl_meritechcapital(articles)
    crawl_stockmarketnerd(articles)
    # crawl_palladium(get_object_or_404(Source, name="Palladium"), "https://www.palladiummag.com/feed/", articles)


@shared_task
def scrape_spotify():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=spotify_sources).only(
        "title", "link", "source"
    )
    spotify_creation_list = []
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        try:
            episodes = spotify.get_episodes(source.external_id)
            episode_items = episodes["items"]
            for episode_item in episode_items:
                title = unescape(episode_item["name"])
                link = episode_item["external_urls"]["spotify"]
                if articles.filter(title=title, link=link, source=source).exists():
                    break
                spotify_creation_list.append(
                    {
                        "title": title,
                        "link": link,
                        "pub_date": timezone.now(),
                        "source": source,
                    }
                )
        except:
            continue
    bulk_create_articles_and_notifications(spotify_creation_list)


@shared_task
def scrape_youtube():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=youtube_sources).only(
        "title", "pub_date", "link", "source"
    )
    youtube_creation_list = []
    for source in youtube_sources:
        channel_data = request_get(
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails"
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
        r = request_get(url)
        data = r.json()
        try:
            items = data["items"]
            for item in items:
                title = unescape(item["snippet"]["title"])
                link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                pub_date = item["snippet"]["publishedAt"]
                if articles.filter(
                    title=title, pub_date=pub_date, link=link, source=source
                ).exists():
                    break
                elif articles.filter(title=title, source=source).count() == 1:
                    article = articles.get(title=title, source=source)
                    article.pub_date = pub_date
                    article.link = link
                    article.save()
                else:
                    youtube_creation_list.append(
                        {
                            "title": title,
                            "link": link,
                            "pub_date": pub_date,
                            "source": source,
                        }
                    )
        except:
            continue
    bulk_create_articles_and_notifications(youtube_creation_list)


@shared_task
def twitter_scrape_followings():
    api = twitter_create_api_settings()
    followings = api.get_friends(count=100)
    for follow in followings:
        name = follow.name
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        elif (
            Source.objects.filter(name=follow.name).exists()
            or Source.objects.filter(slug=slugify(name)).exists()
        ):
            name = follow.name + " - Twitter"
        url = f"https://twitter.com/{follow.screen_name}"
        slug = slugify(name)
        external_id = follow.id
        source = Source.objects.create(
            url=url,
            slug=slug,
            name=name,
            favicon_path=f"home/favicons/{slug}.png",
            paywall="No",
            website=get_object_or_404(Website, name="Twitter"),
            external_id=external_id,
        )
        source_profile_img_create(
            source, follow.profile_image_url_https.replace("_normal", "")
        )


@shared_task
def youtube_get_profile_images():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    for source in youtube_sources:
        try:
            url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
            r = request_get(url)
            data = r.json()
            source_profile_img_create(
                source, data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
            )
        except:
            continue


@shared_task
def spotify_get_profile_images():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    )
    for source in spotify_sources:
        try:
            spotify = SpotifyAPI(client_id, client_secret)
            podcaster = spotify.get_podcaster(source.external_id)
            if "images" in podcaster.keys():
                source_profile_img_create(source, podcaster["images"][0]["url"])
            else:
                continue
        except:
            continue


@shared_task
def old_notifications_delete():
    NotificationMessage.objects.filter(
        date__lte=timezone.now() - timedelta(hours=24)
    ).delete()


@shared_task
def youtube_delete_innacurate_articles():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    youtube_videos = []
    for source in youtube_sources:
        saved_articles_from_source = Article.objects.filter(source=source)
        channel_data = request_get(
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails"
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
        r = request_get(url)
        item_list = []
        next_item = True
        iterations = 0
        while next_item and iterations < 20:
            data = r.json()
            items = data["items"]
            item_list.append(items)
            if "nextPageToken" in data.keys():
                nextPageToken = data["nextPageToken"]
                iterations += 1
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000&pageToken={nextPageToken}"
                r = request_get(url)
            else:
                next_item = False
                break
        for items in item_list:
            try:
                for item in items:
                    title = unescape(item["snippet"]["title"])
                    link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    pub_date = item["snippet"]["publishedAt"]
                    youtube_videos.append(
                        {"title": title, "link": link, "pub_date": pub_date}
                    )
            except:
                continue
        for article in saved_articles_from_source:
            if not any(d["title"] == article.title for d in youtube_videos) or not any(
                d["link"] == article.link
                for d in youtube_videos
                or not any(d["pub_date"] == article.pub_date for d in youtube_videos)
            ):
                article.delete()


@shared_task
def delete_article_duplicates():
    sources = Source.objects.exclude(website__name="Twitter")
    ids_of_duplicate_articles = []
    for source in sources:
        articles_from_source = Article.objects.filter(source=source)
        for article in articles_from_source:
            article_duplicate = articles_from_source.filter(
                title=article.title, pub_date=article.pub_date
            )
            if article_duplicate.count() > 1:
                if article_duplicate.last().article_id not in ids_of_duplicate_articles:
                    ids_of_duplicate_articles.append(
                        article_duplicate.last().article_id
                    )
    Article.objects.filter(article_id__in=ids_of_duplicate_articles).delete()


@shared_task
def delete_tweet_types_empty():
    tweet_types = TweetType.objects.all()
    for type in tweet_types:
        if not type.tweet.all():
            type.delete()


@shared_task
def calc_sim_sources():
    Source.objects.calc_similiar_sources()
    # for source in Source.objects.all():
    #     source.sim_sources.clear()
    #     Source.objects.calc_similiar_sources(source)


@shared_task
def finbrowser_v2_migration():
    for user in User.objects.all():
        if List.objects.filter(creator=user).exists():
            main_list = List.objects.filter(creator=user).first()
            main_list.main = True
            main_list.save()
        else:
            List.objects.create(creator=user, name="Main List", main=True)
        for rating in SourceRating.objects.filter(user=user):
            rating.rating = rating.rating * 2
            rating.save()
        Portfolio.objects.create(user=user, name="Main List", main=True)


@shared_task
def stocks_create_all_companies_json():
    api_key = environ.get("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open("data_next.json", "w") as f:
            for chunk in response.iter_content(chunk_size=1024):
                try:
                    chunk_str = chunk.decode("utf-8", errors="ignore")
                    f.write(chunk_str)
                except UnicodeDecodeError as e:
                    print("UnicodeDecodeError:", e)
    else:
        # handle the error
        print("API call failed with status code:", response.status_code)


@shared_task
def stocks_create_models_from_json():
    with open("all_companies_01042023.json", "r") as f:
        company_data = json.load(f)
    for item in company_data:
        symbol = item["symbol"]
        if (
            item["type"] == "stock"
            and all(char not in symbol for char in ("."))
            and len(symbol) < 7
        ):
            if "-" in symbol:
                symbol = symbol.replace("-", ".")
            full_name = item["name"]
            short_name = full_name
            for word in full_fillerwords:
                short_name = short_name.replace(word, "")
            for word in short_fillerwords:
                short_name = short_name.replace(word, "")
            stock_instance = Stock.objects.filter(ticker=symbol).first()
            try:
                if stock_instance:
                    stock_instance.full_company_name = full_name[:100]
                    stock_instance.short_company_name = short_name[:100]
                    stock_instance.save()
                elif Stock.objects.filter(full_company_name=full_name[:100]).exists():
                    continue
                else:
                    Stock.objects.create(
                        ticker=symbol,
                        full_company_name=full_name[:100],
                        short_company_name=short_name[:100],
                    )
            except Exception as e:
                print(e)
                continue


# @shared_task
# def stocks_create():
#     filename = 'stocks.csv'
#     with open(filename, 'r') as csvfile:
#         fillerwords = [" Inc.", " Corporation", "  & Co.", " Group", " Holding", " Holdings", " Ltd", " plc", " inc", " S.A.B. de C.V.", " S.A. de C.V.", ".com", " Technology", " Corp", " (The)", " International", " Limited", " N.A.", " Technologies", " L.P.", " Co.", " Incoperated", " S.A.", " (NJ)", " p.l.c.", " ,", ",", "."]
#         datareader = csv.reader(csvfile)
#         for row in datareader:
#             if "." in row[0] or "^" in row[0] or Stock.objects.filter(full_company_name=html.unescape(row[1])).exists():
#                 continue
#             ticker = row[0]
#             short_company_name = full_company_name = html.unescape(row[1])
#             for fil in fillerwords:
#                 short_company_name = short_company_name.replace(fil, "")
#             Stock.objects.create(ticker=ticker, full_company_name=full_company_name, short_company_name=short_company_name)


# @shared_task
# def stocks_create_with_nasdaq():
#     filename = 'nasdaq.csv'
#     with open(filename, 'r') as csvfile:
#         full_fillerwords = [" Class D", " American Depositary Shares each representing one-fifth of an Ordinary Share", " common stock", " Warrants", " Ordinary Shares", " ordinary share", " each representing 1/1000th interest in a share of Series I Non-CumulativePreferred Stock","Dep Shs Repstg 1/40th Perp Pfd Ser G", " Fixed-to-Floating Rate Non-Cumulative Perpetual Preferred Stock Series D", " 1 Unit", " Unit", " each representing one", " Ordinary Share", " Class A", " Voting Common Stock", " New Switzerland Registered Shares", " Series D Cumulative Preferred Stock", " Class B Preferred Stock", " Ordinary Shares"," American Depositary Shares",  " American Depositary Share", " Depositary Shares", " Common Shares", " of Beneficial Interest", " Warrant", " Warrants", " Common stock", " Common Shares", " Common Stock", " Series A", " Corp.s", " N.V.s", " American depositary shares each representing two ordinary shares", " AGs-fifth of an", " Redeemable Preferred Stock", " expiring", " and Class B Variable Voting Shares", " Right", ". 1s"]
#         short_fillerwords = [" & Co.", " Company", " Inc.", " Inc", " Corporation", "  & Co.", " Group", " Holdings", " Holding", " Ltd", " plc", " inc", " S.A.B. de C.V.", " S.A. de C.V.", ".com", " Technology", " Corp", " (The)", " International", " Limited", " N.A.", " N.V.", " Technologies", " L.P.", " Co.", " Incoperated", " S.A.", " (NJ)", " p.l.c.", " .s", " Public Companys", " Companys", " S.p.A.s", " S.p.A.",  " B.V.s"]
#         datareader = csv.reader(csvfile)
#         for row in datareader:
#             ticker = row[0]
#             full_company_name = html.unescape(row[1])
#             for fil in full_fillerwords:
#                 full_company_name = full_company_name.replace(fil, "")
#             short_company_name = full_company_name
#             for fil in short_fillerwords:
#                 short_company_name = short_company_name.replace(fil, "")
#                 " ,", ",", "."
#             if "," in short_company_name or "." in short_company_name or "   " in row[1] or "/" in row[1] or "$" in row[1] or "(" in row[1] or "%" in row[1] or "." in row[0] or "^" in row[0] or Stock.objects.filter(full_company_name=full_company_name).exists() or Stock.objects.filter(ticker=ticker).exists() or len(full_company_name) > 45 or len(short_company_name) > 35:
#                 continue
#             Stock.objects.create(ticker=ticker, full_company_name=full_company_name, short_company_name=short_company_name)


# @shared_task
# def delete_articles_without_source():
#     articles = Article.objects.all()
#     for article in articles:
#         if article.source is None:
#             article.delete()
