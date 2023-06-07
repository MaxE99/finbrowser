from __future__ import absolute_import, unicode_literals

# Python imports
from datetime import timedelta
from html import unescape
from time import sleep
from base64 import b64encode
from os import environ
from re import sub as re_sub
from celery import shared_task
from requests import post as request_post
from requests import get as request_get
from boto3 import client


# Django imports
from django.core.cache import cache
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


# Local imports
from apps.logic.services import (
    bulk_create_articles_and_notifications,
    notifications_create,
    create_articles_from_feed,
    source_profile_img_create,
    twitter_create_api_settings,
    tweet_type_create,
    article_creation_check,
    get_substack_info,
)
from apps.article.models import Article, TweetType
from apps.home.models import NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source, SourceRating, Sector, SourceTag


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
        if client_id is None or client_secret is None:
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
        request = request_post(
            self.token_url,
            data=self.get_token_data(),
            headers=self.get_token_headers(),
            timeout=10,
        )
        if request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        data = request.json()
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
        if token is None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_episodes(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        request = request_get(lookup_url, headers=headers, timeout=10)
        if request.status_code not in range(200, 299):
            return {}
        return request.json()

    def get_podcaster(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        r = request_get(lookup_url, headers=headers, timeout=10)
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
        except Exception as _:
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
        "title", "pub_date", "source", "link"
    )
    for source in substack_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)
        sleep(6)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="SeekingAlpha")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=seekingalpha_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in seekingalpha_sources:
        feed_url = f"{source.url}.xml"
        create_articles_from_feed(source, feed_url, articles)
        sleep(15)


@shared_task
def scrape_other_websites():
    other_sources = (
        Source.objects.filter(website=get_object_or_404(Website, name="Other"))
        .exclude(external_id__isnull=False)
        .only("source_id", "url", "website")
    )
    articles = Article.objects.filter(source__in=other_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in other_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def scrape_forbes():
    forbes_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Forbes")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=forbes_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in forbes_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)
        sleep(5)


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
                # SpotifyAPI release_date only has date precision, so it always shows midnight => therefore better to use current time of scrapping
                spotify_creation_list, article_exists = article_creation_check(
                    spotify_creation_list, articles, title, source, link
                )
                if article_exists:
                    break
        except Exception as _:
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
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
            timeout=10,
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
        request = request_get(url, timeout=10)
        data = request.json()
        try:
            items = data["items"]
            for item in items:
                title = unescape(item["snippet"]["title"])
                link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                pub_date = item["snippet"]["publishedAt"]
                youtube_creation_list, article_exists = article_creation_check(
                    youtube_creation_list,
                    articles,
                    title,
                    source,
                    link,
                    pub_date=pub_date,
                )
                if article_exists:
                    break
        except Exception as _:
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
        if (
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
            request = request_get(url, timeout=10)
            data = request.json()
            source_profile_img_create(
                source, data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
            )
        except Exception as _:
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
        except Exception as _:
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
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
            timeout=10,
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
        request = request_get(url, timeout=10)
        item_list = []
        next_item = True
        iterations = 0
        while next_item and iterations < 20:
            data = request.json()
            items = data["items"]
            item_list.append(items)
            if "nextPageToken" in data.keys():
                next_page_token = data["nextPageToken"]
                iterations += 1
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000&pageToken={next_page_token}"
                request = request_get(url, timeout=10)
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
            except Exception as _:
                continue
        for article in saved_articles_from_source:
            if not any(d["title"] == article.title for d in youtube_videos) or not any(
                d["link"] == article.link
                for d in youtube_videos
                or not any(d["pub_date"] == article.pub_date for d in youtube_videos)
            ):
                article.delete()


@shared_task
def delete_tweet_types_empty():
    tweet_types = TweetType.objects.all()
    for tweet_type in tweet_types:
        if not tweet_type.tweet.all():
            tweet_type.delete()


@shared_task
def calc_sim_sources():
    Source.objects.calc_similiar_sources()


@shared_task
def substack_scrape_accounts():
    new_substack_sources = []
    for source_url in new_substack_sources:
        try:
            print(source_url)
            name, img_url = get_substack_info(source_url)
            if (
                Source.objects.filter(name=name).exists()
                or Source.objects.filter(slug=slugify(name)).exists()
            ):
                name = name + " - Substack"
            source = Source.objects.create(
                url=source_url,
                slug=slugify(name),
                name=name,
                favicon_path=f"home/favicons/{slugify(name)}.png",
                paywall="Yes",
                website=get_object_or_404(Website, name="Substack"),
            )
            source_profile_img_create(source, img_url)
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=source,
                rating=7,
            )
            sleep(5)
        except Exception as error:
            print(f"Scrapping {source_url} has caused this error: ")
            print(error)
            continue


@shared_task
def seeking_alpha_scrape_accounts():
    new_sources = [
        {
            "url": "https://seekingalpha.com/author/best-anchor-stocks",
            "name": "Best Anchor Stocks",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/205/028/extra_large_pic.png",
            "rating": 8,
            "sector": "Tech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/riyado-sofian",
            "name": "Riyado Sofian",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/050/787/769/extra_large_pic.png",
            "rating": 9,
            "sector": "Tech",
            "tags": ["Deep-Dives", "Business Breakdowns"],
        },
        {
            "url": "https://seekingalpha.com/author/busted-ipo-forum",
            "name": "Busted IPO Forum",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/048/630/172/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/carles-diaz-caron",
            "name": "Carles Diaz Caron",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/049/210/517/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Dividend Investor"],
        },
        {
            "url": "https://seekingalpha.com/author/jonquil-capital",
            "name": "Carles Diaz Caron",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/047/512/389/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/danil-sereda",
            "name": "Danil Sereda",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/049/513/514/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/out-of-ignorance",
            "name": "Out of Ignorance",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/003/024/641/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/stephen-tobin",
            "name": "Stephen Tobin",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/047/437/728/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/philip-eriksson",
            "name": "Philip Eriksson",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/051/580/423/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/galzus-research",
            "name": "Galzus Research",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/330/420/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": ["Industry Insider"],
        },
        {
            "url": "https://seekingalpha.com/author/biotechvalley-insights",
            "name": "BiotechValley Insights",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/049/426/560/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": ["Industry Insider"],
        },
        {
            "url": "https://seekingalpha.com/author/david-zanoni",
            "name": "David Zanoni",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/371/238/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/vision-and-value",
            "name": "Vision and Value",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/047/560/554/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/michigan-value-investor",
            "name": "Michigan Value Investor",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/213/542/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/d-s-leach-c-e-leach",
            "name": "D.S. Leach & C.E. Leach",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/022/419/601/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/welbeck-ash-research",
            "name": "Welbeck Ash Research",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/055/358/919/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/gs-analytics",
            "name": "GS Analytics",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/015/666/062/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/the-profit-detective",
            "name": "The Profit Detective",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/058/425/273/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/gold-panda",
            "name": "Gold Panda",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/036/303/466/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/double-dividend-stocks",
            "name": "Double Dividend Stocks",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/000/418/011/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Dividend Investor"],
        },
        {
            "url": "https://seekingalpha.com/author/zach-bristow",
            "name": "Zach Bristow",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/051/411/522/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/more-ideas-than-money",
            "name": "More Ideas Than Money",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/018/013/272/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/courage-conviction-investing",
            "name": "Courage & Conviction Investing",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/001/099/377/extra_large_pic.png",
            "rating": 8,
            "sector": "Small Cap",
            "tags": ["Financial Analyst"],
        },
        {
            "url": "https://seekingalpha.com/author/stephen-ayers",
            "name": "Stephen Ayers",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/048/050/289/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/patrik-mackovych",
            "name": "Patrik Mackovych",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/050/644/761/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Financial Analyst"],
        },
        {
            "url": "https://seekingalpha.com/author/deep-tech-insights",
            "name": "Deep Tech Insights",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/055/230/498/extra_large_pic.png",
            "rating": 8,
            "sector": "Tech",
            "tags": ["Financial Analyst"],
        },
        {
            "url": "https://seekingalpha.com/author/cameron-fen",
            "name": "Cameron Fen",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/004/043/931/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/malak-investment-ideas",
            "name": "Malak Investment Ideas",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/057/791/104/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Former Finance Career"],
        },
        {
            "url": "https://seekingalpha.com/author/stratos-capital-partners",
            "name": "Stratos Capital Partners",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/025/338/263/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Research Service", "Senior Finance Role"],
        },
        {
            "url": "https://seekingalpha.com/author/ahan-analytics",
            "name": "Ahan Analytics",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/000/029/389/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/ian-bezek",
            "name": "Ian Bezek",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/000/171/953/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Former Finance Career"],
        },
        {
            "url": "https://seekingalpha.com/author/raul-shah",
            "name": "Raul Shah",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/034/511/865/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/fernando-batista-costa",
            "name": "Fernando Batista Costa",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/053/529/963/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/daan-rijnberk",
            "name": "Daan Rijnberk",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/767/760/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/elliott-gue",
            "name": "Elliott Gue",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/470/666/extra_large_pic.png",
            "rating": 9,
            "sector": "Energy",
            "tags": ["Deep-Dives", "Business Breakdowns"],
        },
        {
            "url": "https://seekingalpha.com/author/jim-sloan",
            "name": "Jim Sloan",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/546/142/extra_large_pic.png",
            "rating": 9,
            "sector": "Generalists",
            "tags": ["Company Specialist"],
        },
        {
            "url": "https://seekingalpha.com/author/goldstreetbets-research",
            "name": "GoldStreetBets Research",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/056/953/874/extra_large_pic.png",
            "rating": 8,
            "sector": "Materials",
            "tags": ["Former Finance Career"],
        },
        {
            "url": "https://seekingalpha.com/author/istj-investor",
            "name": "ISTJ Investor",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/008/082/481/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/lane-simonian",
            "name": "Lane Simonian",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/023/872/453/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": ["Industry Insider"],
        },
        {
            "url": "https://seekingalpha.com/author/from-growth-to-value",
            "name": "From Growth to Value",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/038/067/716/extra_large_pic.png",
            "rating": 8,
            "sector": "Tech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/column-research",
            "name": "Column Research",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/051/776/427/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/cook-capital-management",
            "name": "Cook Capital Management",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/031/633/755/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Special Situations"],
        },
        {
            "url": "https://seekingalpha.com/author/the-energy-realist",
            "name": "The Energy Realist",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/052/907/151/extra_large_pic.png",
            "rating": 8,
            "sector": "Energy",
            "tags": ["Chartered Financial Analyst (CFA)"],
        },
        {
            "url": "https://seekingalpha.com/author/john-overstreet",
            "name": "John Overstreet",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/001/066/978/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/oyat",
            "name": "Oyat",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/019/065/331/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Investment Fund"],
        },
        {
            "url": "https://seekingalpha.com/author/r-paul-drake",
            "name": "R. Paul Drake",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/049/965/383/extra_large_pic.png",
            "rating": 8,
            "sector": "Housing & REITs",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/deep-value-ideas",
            "name": "Deep Value Ideas",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/049/694/823/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Dividend Investor", "Value Investor"],
        },
        {
            "url": "https://seekingalpha.com/author/eugenio-catone",
            "name": "Eugenio Catone",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/056/207/090/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/inversiones-apartado",
            "name": "Inversiones Apartado",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/049/792/172/extra_large_pic.png",
            "rating": 8,
            "sector": "Energy",
            "tags": ["LATAM Expert"],
        },
        {
            "url": "https://seekingalpha.com/author/ip-banking-research",
            "name": "IP Banking Research",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/032/904/585/extra_large_pic.png",
            "rating": 8,
            "sector": "Financials",
            "tags": ["Special Situations"],
        },
        {
            "url": "https://seekingalpha.com/author/damon-judd",
            "name": "Damon Judd",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/000/329/016/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/rob-barnett",
            "name": "Rob Barnett",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/006/691/401/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/sarel-oberholster",
            "name": "Sarel Oberholster",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/000/488/424/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Deep-Dives"],
        },
        {
            "url": "https://seekingalpha.com/author/the-affluent-tortoise",
            "name": "The Affluent Tortoise",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/007/506/841/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Value Investor"],
        },
        {
            "url": "https://seekingalpha.com/author/siyu-li",
            "name": "Siyu Li",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/000/034/047/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/tian-li",
            "name": "Tian Li",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/453/340/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/tomas-andrade-campanini",
            "name": "Tomas Andrade Campanini",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/051/700/268/extra_large_pic.png",
            "rating": 8,
            "sector": "Small Cap",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/the-wealth-wizard",
            "name": "The Wealth Wizard",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/058/065/543/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/jeremy-lakosh",
            "name": "Jeremy Lakosh",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/020/858/741/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Dividend Investor"],
        },
        {
            "url": "https://seekingalpha.com/author/ivo-kolchev",
            "name": "Ivo Kolchev",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/044/733/396/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/derek-pitman-betsy-yang",
            "name": "Derek Pitman & Betsy Yang",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/049/482/691/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/ufd-capital",
            "name": "UFD Capital",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/057/844/100/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Investment Advisory"],
        },
        {
            "url": "https://seekingalpha.com/author/oakoff-investments",
            "name": "Oakoff Investments",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/053/838/465/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["Financial Analyst"],
        },
        {
            "url": "https://seekingalpha.com/author/herding-value",
            "name": "Herding Value",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/048/469/061/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/david-ksir",
            "name": "David Ksir",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/057/823/937/extra_large_pic.png",
            "rating": 8,
            "sector": "Housing & REITs",
            "tags": ["Former Finance Career"],
        },
        {
            "url": "https://seekingalpha.com/author/rational-expectations",
            "name": "Rational Expectations",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/434/482/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/zmk-capital",
            "name": "ZMK Capital",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/037/078/886/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/nexus-research",
            "name": "Nexus Research",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/049/821/292/extra_large_pic.png",
            "rating": 8,
            "sector": "Tech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/the-pineapple-investor",
            "name": "The Pineapple Investor",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/048/157/999/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/simple-digressions",
            "name": "Simple Digressions",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/000/243/441/extra_large_pic.png",
            "rating": 8,
            "sector": "Materials",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/bellasooa-research",
            "name": "Bellasooa Research",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/056/362/683/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["EU Expert"],
        },
        {
            "url": "https://seekingalpha.com/author/kgr-ventures",
            "name": "KGR Ventures",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/005/135/241/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["China Expert"],
        },
        {
            "url": "https://seekingalpha.com/author/c-c-abbott",
            "name": "C.C. Abbott",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/047/985/150/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": ["Industry Insider"],
        },
        {
            "url": "https://seekingalpha.com/author/david-alton-clark",
            "name": "David Alton Clark",
            "profile_pic": "https://static.seekingalpha.com/images/users_profile/000/790/828/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/bang-for-the-buck",
            "name": "Bang for the Buck",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/048/701/869/extra_large_pic.png",
            "rating": 8,
            "sector": "Materials",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/joseph-l-shaefer",
            "name": "Joseph L. Shaefer",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/000/142/982/extra_large_pic.png",
            "rating": 8,
            "sector": "Materials",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/christoph-liu",
            "name": "Christoph Liu",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/049/419/486/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["EU Expert"],
        },
        {
            "url": "https://seekingalpha.com/author/looking-for-diogenes",
            "name": "Looking For Diogenes",
            "profile_pic": "https://static3.seekingalpha.com/images/users_profile/003/561/631/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/edward-zhang",
            "name": "Edward Zhang",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/048/023/073/extra_large_pic.png",
            "rating": 8,
            "sector": "Biotech",
            "tags": [],
        },
        {
            "url": "https://seekingalpha.com/author/labutes-ir",
            "name": "Labutes IR",
            "profile_pic": "https://static1.seekingalpha.com/images/users_profile/001/104/021/extra_large_pic.png",
            "rating": 8,
            "sector": "Generalists",
            "tags": ["EU Expert", "Former Finance Career"],
        },
        {
            "url": "https://seekingalpha.com/author/liang-zhao-cfa",
            "name": "Liang Zhao, CFA",
            "profile_pic": "https://static2.seekingalpha.com/images/users_profile/044/109/686/extra_large_pic.png",
            "rating": 8,
            "sector": "Tech",
            "tags": ["China Expert", "Chartered Financial Analyst (CFA)"],
        },
    ]

    failed_scrapping = []
    for source in new_sources:
        try:
            print(source)
            name_of_new_source = source["name"]
            created_source = Source.objects.create(
                url=source["url"],
                slug=slugify(name_of_new_source),
                name=name_of_new_source,
                favicon_path=f"home/favicons/{slugify(name_of_new_source)}.png",
                paywall="Yes",
                website=get_object_or_404(Website, name="SeekingAlpha"),
                content_type="Analysis",
                sector=get_object_or_404(Sector, name=source["sector"]),
            )
            if len(source["tags"]):
                for tag in source["tags"]:
                    created_source.tags.add(get_object_or_404(SourceTag, name=tag))
            source_profile_img_create(created_source, source["profile_pic"])
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=created_source,
                rating=source["rating"],
            )
            sleep(5)
        except Exception as error:
            failed_scrapping.append(name_of_new_source)
            print(f"Scrapping {name_of_new_source} has caused this error: ")
            print(error)
            continue
    print("The following sources could not be scrapped: ")
    for source in failed_scrapping:
        print(source)


# =================================================================================
# Tasks that need to be used from time to time
# =================================================================================


# @shared_task
# def stocks_create_all_companies_json():
#     api_key = environ.get("FMP_API_KEY")
#     url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
#     response = request_get(url, stream=True, timeout=10)
#     if response.status_code == 200:
#         with open("data_next.json", "w") as f:
#             for chunk in response.iter_content(chunk_size=1024):
#                 try:
#                     chunk_str = chunk.decode("utf-8", errors="ignore")
#                     f.write(chunk_str)
#                 except UnicodeDecodeError as err:
#                     print("UnicodeDecodeError:", err)


# @shared_task
# def stocks_create_models_from_json():
#     with open("all_companies_01042023.json", "r") as f:
#         company_data = json.load(f)
#     for item in company_data:
#         symbol = item["symbol"]
#         if (
#             item["type"] == "stock"
#             and all(char not in symbol for char in ("."))
#             and len(symbol) < 7
#         ):
#             if "-" in symbol:
#                 symbol = symbol.replace("-", ".")
#             full_name = item["name"]
#             short_name = full_name
#             for word in full_fillerwords:
#                 short_name = short_name.replace(word, "")
#             for word in short_fillerwords:
#                 short_name = short_name.replace(word, "")
#             stock_instance = Stock.objects.filter(ticker=symbol).first()
#             try:
#                 if stock_instance:
#                     stock_instance.full_company_name = full_name[:100]
#                     stock_instance.short_company_name = short_name[:100]
#                     stock_instance.save()
#                 elif Stock.objects.filter(full_company_name=full_name[:100]).exists():
#                     continue
#                 else:
#                     Stock.objects.create(
#                         ticker=symbol,
#                         full_company_name=full_name[:100],
#                         short_company_name=short_name[:100],
#                     )
#             except Exception as e:
#                 continue


# @shared_task
# def find_english_words():
#     # Load the words from the text file
#     with open("words.txt", "r") as f:
#         words = set(line.strip() for line in f)

#     # Create an empty list to store the matching words
#     english_words = []

#     # Loop through all instances of the Stock model
#     for stock in Stock.objects.all():
#         # Check if the ticker is in the words set
#         if stock.ticker.lower() in words:
#             english_words.append(stock.ticker.lower())
#         # Check if the short_company_name is in the words set
#         if stock.short_company_name.lower() in words:
#             english_words.append(stock.short_company_name.lower())

#     # Write the English words to a new Python file
#     with open("english_words.py", "w") as f:
#         f.write("english_words = {}\n".format(english_words))


# @shared_task
# def delete_article_duplicates():
#     sources = Source.objects.exclude(website__name="Twitter")
#     for source in sources:
#         ids_of_duplicate_articles = []
#         try:
#             articles_from_source = Article.objects.filter(source=source).order_by(
#                 "pub_date"
#             )
#             for article in articles_from_source:
#                 title_duplicates = articles_from_source.filter(title=article.title)
#                 duplicates = title_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         title_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             title_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#                 link_duplicates = articles_from_source.filter(link=article.link)
#                 duplicates = link_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         link_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             link_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#         except Exception as error:
#             print(error)
#         Article.objects.filter(article_id__in=ids_of_duplicate_articles).delete()


# @shared_task
# def forbes_scrape_accounts():
#     new_forbes_sources = []
#     failed_scrapping = []
#     for source_url in new_forbes_sources:
#         try:
#             print(source_url)
#             name, img_url = get_forbes_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#             ):
#                 name = name + " - Forbes"
#             source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.png",
#                 paywall="Semi",
#                 website=get_object_or_404(Website, name="Forbes"),
#                 content_type="News",
#             )
#             source_profile_img_create(source, img_url)
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=source,
#                 rating=7,
#             )
#             sleep(5)
#         except Exception as error:
#             failed_scrapping.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)
