from __future__ import absolute_import, unicode_literals
# Django imports
from django.core.cache import cache
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.template.defaultfilters import slugify
# Python imports
import tweepy
from datetime import timedelta
import logging
from celery.signals import after_setup_logger
import html
import time
import requests
import base64
import os
import boto3
import re
from apps.home.views import TWITTER
# Local imports
from apps.logic.services import notifications_create, create_articles_from_feed, source_profile_img_create, tweet_img_upload, initial_tweet_img_path_upload
from apps.article.models import Article, TweetType
from apps.home.models import NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source
from apps.scrapper.web_crawler import crawl_thegeneralist, crawl_ben_evans, crawl_meritechcapital, crawl_stockmarketnerd

s3 = boto3.client('s3')

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger = logging.getLogger(__name__)


class SpotifyAPI(object):
    access_token = None
    access_token_expires = now()
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
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credientals()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }   

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        r = requests.post(self.token_url, data=self.get_token_data(), headers=self.get_token_headers())
        if r.status_code not in range(200,299):
            raise Exception("Could not authenticate client.")
        data = r.json()
        expires_in = data['expires_in']
        expires = now() + timedelta(seconds=expires_in)
        self.access_token = data['access_token']
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now() 
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        if expires < now():
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_episodes(self, id):       
        access_token = self.get_access_token()
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200,299):
            return {} 
        return r.json() 

    def get_podcaster(self, id):       
        access_token = self.get_access_token()
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200,299):
            return {} 
        return r.json() 


@shared_task
def scrape_twitter():    
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    last_id = cache.get('last_id')
    if last_id:
        statuses = api.home_timeline(count=200, tweet_mode='extended', since_id=last_id, include_entities=True) 
    else:
        statuses = api.home_timeline(count=200, tweet_mode='extended', include_entities=True) 
    existing_tweets = Article.objects.filter(external_id__isnull=False).values_list('external_id', flat=True)
    sources = Source.objects.all() 
    tweet_creation_list = []
    for status in statuses:
        try:
            tweet_external_id = status.id
            if str(tweet_external_id) not in existing_tweets:
                twitter_user_id = status.user.id
                if sources.filter(external_id=twitter_user_id).exists():
                    title = re.sub(r'http\S+', '', html.unescape(status.full_text))
                    link = f'https://twitter.com/{status.user.screen_name}/status/{tweet_external_id}'
                    pub_date = status.created_at
                    tweet_type = TweetType.objects.create(type = "Basic")
                    if 'media' in status.entities:
                        if 'media_url_https' in status.entities['media'][0]:
                            tweet_type.type = "Image"
                            tweet_type = tweet_img_upload(tweet_type, status.entities['media'][0]['media_url_https'])
                    elif len(status.entities['urls']) > 0:
                        if 'expanded_url' in status.entities['urls'][0]:
                            title = html.unescape(status.full_text) # With links I don't escape the title
                            tweet_type.type = "Link"
                            tweet_type.link = status.entities['urls'][0]['expanded_url']
                    in_reply_to_user_id = status.in_reply_to_user_id
                    if hasattr(status, "retweeted_status"):
                        tweet_type.pub_date = status.retweeted_status.created_at
                        tweet_type.text = re.sub(r'http\S+', '', html.unescape(status.retweeted_status.full_text))
                        tweet_type.author = status.retweeted_status.user.name
                        if 'media' in status.retweeted_status._json['entities']:
                            if 'media_url_https' in status.retweeted_status._json['entities']['media'][0]:
                                tweet_type.image_path = None # Despite the status being a retweet Twitter sometimes sends a picture in the media dictionary which would lead to the image being shown 2 times
                                tweet_type = initial_tweet_img_path_upload(tweet_type, status.retweeted_status._json['entities']['media'][0]['media_url_https'])
                        tweet_type.type = "Retweet"
                    elif in_reply_to_user_id != None and in_reply_to_user_id != twitter_user_id:
                        tweet_reply_id = status.in_reply_to_status_id
                        tweet_reply_info = api.get_status(id=tweet_reply_id, tweet_mode='extended')
                        tweet_type.pub_date = tweet_reply_info.created_at
                        tweet_type.text = re.sub(r'http\S+', '', html.unescape(tweet_reply_info.full_text))
                        tweet_type.author = tweet_reply_info.user.name
                        if hasattr(tweet_reply_info.entities, 'media'):
                            if 'media_url_https' in tweet_reply_info.entities['media'][0]:
                                tweet_type = initial_tweet_img_path_upload(tweet_type, tweet_reply_info.entities['media'][0]['media_url_https'])
                        tweet_type.type = "Reply"
                    elif status.is_quote_status == True:
                        tweet_type.pub_date = status.quoted_status.created_at
                        tweet_type.text = re.sub(r'http\S+', '', html.unescape(status.quoted_status.full_text))
                        tweet_type.author = status.quoted_status.user.name
                        if 'media' in status.quoted_status._json['entities']:
                            if 'media_url_https' in status.quoted_status._json['entities']['media'][0]:
                                tweet_type = initial_tweet_img_path_upload(tweet_type, status.quoted_status._json['entities']['media'][0]['media_url_https'])
                        tweet_type.type = "Quote"
                    tweet_type.save()
                    tweet_creation_list.append({'source': twitter_user_id, 'title': title, 'link': link, 'pub_date': pub_date, 'external_id': tweet_external_id, 'tweet_type': tweet_type})
            else:
                break
            last_id = tweet_external_id
        except:
            continue
    cache.set('last_id', last_id)
    new_articles = [
        Article(
            title=new_tweet['title'],
            link=new_tweet['link'],
            pub_date=new_tweet['pub_date'],
            source=sources.get(external_id=new_tweet['source']),
            external_id=new_tweet['external_id'],
            tweet_type=new_tweet['tweet_type']
        )
        for new_tweet in tweet_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(website=get_object_or_404(Website, name="Substack"))
    articles = Article.objects.all()
    for source in substack_sources:
        feed_url = f'{source.url}feed'
        create_articles_from_feed(source, feed_url, articles)
        time.sleep(30)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(website=get_object_or_404(Website, name="SeekingAlpha"))
    articles = Article.objects.all()
    for source in seekingalpha_sources:
        feed_url = f'{source.url}.xml'
        create_articles_from_feed(source, feed_url, articles)
        time.sleep(60)


@shared_task
def scrape_other_websites():
    other_sources = Source.objects.filter(website=get_object_or_404(Website, name="Other")).exclude(external_id__isnull=False)
    articles = Article.objects.all()
    for source in other_sources:
        feed_url = f'{source.url}feed'
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def scrape_news():
    news_sources = Source.objects.filter(news=True)
    articles = Article.objects.all()
    for source in news_sources:
        feed_url = f'{source.url}feed'
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def crawl_websites():
    articles = Article.objects.all()
    crawl_thegeneralist(articles)
    crawl_ben_evans(articles)
    crawl_meritechcapital(articles)
    crawl_stockmarketnerd(articles)


@shared_task
def scrape_spotify():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    articles = Article.objects.all()
    spotify_creation_list = []
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        try:
            episodes = spotify.get_episodes(source.external_id)
            episode_items = episodes['items']
            for episode_item in episode_items:
                title = html.unescape(episode_item['name'])
                link = episode_item['external_urls']['spotify']
                if articles.filter(title=title, link=link, source=source).exists():
                    break
                else:
                    spotify_creation_list.append({'title': title, 'link': link, 'pub_date': now(), 'source': source})
        except:
            continue
    new_articles = [
        Article(
            title=new_article['title'],
            link=new_article['link'],
            pub_date=new_article['pub_date'],
            source=new_article['source']
        )
        for new_article in spotify_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def scrape_youtube():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    articles = Article.objects.all()
    youtube_creation_list = []
    for source in youtube_sources:
        channel_data = requests.get(f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails").json()
        upload_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
        r = requests.get(url)
        data = r.json()
        try:
            items = data['items']
            for item in items:
                title = html.unescape(item['snippet']['title'])
                link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                pub_date = item['snippet']['publishedAt']
                if articles.filter(title=title, pub_date=pub_date, link=link, source=source).exists():
                    break
                elif articles.filter(title=title, source=source).count() == 1:
                    article = articles.get(title=title, source=source)
                    article.pub_date = pub_date
                    article.link = link
                    article.save()
                else:
                    youtube_creation_list.append({'title': title, 'link': link, 'pub_date': pub_date, 'source': source})
        except:
            continue
    new_articles = [
        Article(
            title=new_article['title'],
            link=new_article['link'],
            pub_date=new_article['pub_date'],
            source=new_article['source']
        )
        for new_article in youtube_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def twitter_scrape_followings():
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    followings = api.get_friends(count=100)
    for follow in followings:
        name = follow.name
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        elif Source.objects.filter(name=follow.name).exists():
            name = follow.name + " - Twitter"
        url = f'https://twitter.com/{follow.screen_name}'
        slug = slugify(name)
        external_id = follow.id
        source = Source.objects.create(url=url, slug=slug, name=name, favicon_path=f'home/favicons/{slug}.png', paywall='No', website=get_object_or_404(Website, name="Twitter"), external_id=external_id)
        source_profile_img_create(source, follow.profile_image_url_https.replace("_normal", ""))


@shared_task
def youtube_get_profile_images():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    for source in youtube_sources:
        try:
            url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
            r = requests.get(url)
            data = r.json()
            source_profile_img_create(source, data['items'][0]['snippet']['thumbnails']['medium']['url'])
        except:
            continue


@shared_task
def spotify_get_profile_images():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    for source in spotify_sources:
        try:
            spotify = SpotifyAPI(client_id, client_secret)
            podcaster = spotify.get_podcaster(source.external_id)
            if "images" in podcaster.keys():
                source_profile_img_create(source, podcaster['images'][0]['url'])
            else:
                continue
        except:
            continue


@shared_task
def old_notifications_delete():
    NotificationMessage.objects.filter(date__lte=now()-timedelta(hours=24)).delete()


@shared_task
def youtube_delete_innacurate_articles():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    youtube_videos = []
    for source in youtube_sources:
        saved_articles_from_source = Article.objects.filter(source=source)
        channel_data = requests.get(f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails").json()
        upload_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
        r = requests.get(url)
        item_list = []
        next_item = True
        iterations = 0
        while next_item and iterations<20:
            data = r.json()
            items = data['items']
            item_list.append(items)
            if "nextPageToken" in data.keys():
                nextPageToken = data["nextPageToken"]
                iterations += 1
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000&pageToken={nextPageToken}"
                r = requests.get(url)
            else:
                next_item = False
                break
        for items in item_list:
            try:
                for item in items:
                    title = html.unescape(item['snippet']['title'])
                    link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    pub_date = item['snippet']['publishedAt']
                    youtube_videos.append({'title': title, 'link': link, 'pub_date': pub_date})
            except:
                continue
        for article in saved_articles_from_source:
            if not any(d['title'] == article.title for d in youtube_videos) or not any(d['link'] == article.link for d in youtube_videos or not any(d['pub_date'] == article.pub_date for d in youtube_videos)):
                article.delete()


@shared_task
def delete_article_duplicates():
    sources = Source.objects.exclude(website=TWITTER)
    ids_of_duplicate_articles = []
    for source in sources:
        articles_from_source = Article.objects.filter(source=source)
        for article in articles_from_source:
            article_double_title_and_link = articles_from_source.filter(title=article.title, link=article.link)
            article_double_title_and_date = articles_from_source.filter(title=article.title, pub_date=article.pub_date)
            if article_double_title_and_link.count() > 1:
                if article_double_title_and_link.last().article_id not in ids_of_duplicate_articles:
                    ids_of_duplicate_articles.append(article_double_title_and_link.last().article_id)
            elif article_double_title_and_date.count() > 1:
                if article_double_title_and_date.last().article_id not in ids_of_duplicate_articles:
                    ids_of_duplicate_articles.append(article_double_title_and_date.last().article_id)
    Article.objects.filter(article_id__in=ids_of_duplicate_articles).delete()


@shared_task
def delete_tweet_types_empty():
    tweet_types = TweetType.objects.all()
    for type in tweet_types:
        if not type.tweet.all():
            type.delete()

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