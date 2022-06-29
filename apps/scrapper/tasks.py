from __future__ import absolute_import, unicode_literals
# Django imports
from django.core.cache import cache
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.conf import settings
# Python imports
import tweepy
from datetime import timedelta
import logging
from celery.signals import after_setup_logger
import html
import time
import requests
import environ
import base64
import urllib.request
import os
import boto3
# Local imports
from apps.logic.services import notifications_create, create_articles_from_feed
from apps.article.models import Article
from apps.home.models import Notification, NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source

env = environ.Env()
environ.Env.read_env()

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
        statuses = api.home_timeline(count=200, tweet_mode='extended', since_id=last_id)
    else:
        statuses = api.home_timeline(count=200, tweet_mode='extended')
    articles = Article.objects.all()
    sources = Source.objects.all()
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    for status in statuses:
        if articles.filter(external_id=status.id).exists():
            continue
        else:
            title = html.unescape(status.full_text)
            link = f'https://twitter.com/{status.user.screen_name}/status/{status.id}'
            pub_date = status.created_at
            if sources.filter(external_id=status.user.id).exists():
                source = sources.get(external_id=status.user.id)
                external_id = status.id
                article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source, external_id=external_id)
                notifications_create(source, article, notifications, notification_messages)
            else:
                continue
        last_id = status.id
    cache.set('last_id', last_id)
    for notification_message in notification_messages:
        if (now() - notification_message.date) > timedelta(hours=24):
            notification_message.delete()


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(website=get_object_or_404(Website, name="Substack"))
    articles = Article.objects.all()
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    for source in substack_sources:
        feed_url = f'{source.url}feed'
        create_articles_from_feed(source, feed_url, articles, notifications, notification_messages)
        time.sleep(30)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(website=get_object_or_404(Website, name="SeekingAlpha"))
    articles = Article.objects.all()
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    for source in seekingalpha_sources:
        feed_url = f'{source.url}.xml'
        create_articles_from_feed(source, feed_url, articles, notifications, notification_messages)
        time.sleep(60)


@shared_task
def scrape_spotify():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    articles = Article.objects.all()
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        episodes = spotify.get_episodes(source.external_id)
        episode_items = episodes['items']
        for episode_item in episode_items:
            title = html.unescape(episode_item['name'])
            link = episode_item['external_urls']['spotify']
            if articles.filter(title=title, link=link, source=source).exists():
                break
            else:
                article = Article.objects.create(title=episode_item['name'], link=episode_item['external_urls']['spotify'], pub_date=now(), source=source)
                notifications_create(source, article, notifications, notification_messages)
            
@shared_task
def scrape_youtube():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    articles = Article.objects.all()
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    for source in youtube_sources:
        url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={source.external_id}&part=snippet,id&order=date&maxResults=20'
        r = requests.get(url)
        data = r.json()
        try:
            items = data['items']
            for item in items:
                title = html.unescape(item['snippet']['title'])
                link = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                pub_date = item['snippet']['publishedAt']
                if articles.filter(title=title, pub_date=pub_date, link=link, source=source).exists():
                    break
                else:
                    article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                    notifications_create(source, article, notifications, notification_messages)
        except:
            continue

@shared_task
def spotify_get_profile_images():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        podcaster = spotify.get_podcaster(source.external_id)
        urllib.request.urlretrieve(podcaster['images'][0]['url'], os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{source.slug}.png'))
        favicon_path = f'home/favicons/{source.slug}.png'
        source.favicon_path = favicon_path
        source.save()


@shared_task
def twitter_scrape_followings():
    from apps.source.models import Source
    # assign the values accordingly
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)
    # calling the api 
    api = tweepy.API(auth)
    # fetching the statuses
    followings = api.get_friends(count=100)
    for follow in followings:
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        else:
            url = f'https://twitter.com/{follow.screen_name}'
            slug = follow.screen_name
            name = follow.name
            external_id = follow.id
            with urllib.request.urlopen(follow.profile_image_url_https.replace("_normal", "")) as url:
                profile_image_file = url.read()
            s3 = boto3.client('s3')
            with open(profile_image_file, "rb") as f:
                s3.upload_fileobj(f, "django-testbucket24061436", os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{slug}.png'))
            # urllib.request.urlretrieve(follow.profile_image_url_https.replace("_normal", ""), os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{slug}.png'))
            favicon_path = f'home/favicons/{slug}.png'
            Source.objects.create(url=url, slug=slug, name=name, favicon_path=favicon_path, paywall='No', website=get_object_or_404(Website, name="Twitter"), external_id=external_id)

@shared_task
def youtube_get_profile_images():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    for source in youtube_sources:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
        r = requests.get(url)
        data = r.json()
        favicon = data['items'][0]['snippet']['thumbnails']['medium']['url']
        urllib.request.urlretrieve(favicon, os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{source.slug}.png'))
        favicon_path = f'home/favicons/{source.slug}.png'
        source.favicon_path = favicon_path
        source.save()


