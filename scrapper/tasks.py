from __future__ import absolute_import, unicode_literals
# Django imports
from django.core.cache import cache
from celery import shared_task
from django.shortcuts import get_object_or_404
# Python imports
import tweepy
from datetime import datetime, timedelta, timezone
import logging
from celery.signals import after_setup_logger
import html
import time
import base64
import requests
# Local imports
from home.logic.services import notifications_create, create_articles_from_feed
from home.models import Article, Source
from accounts.models import Website


client_id = 'b0b3c71663ef4c7bb1bcac4cfb1a0a78'
client_secret = '7096cbb406474c42a2357500356f3663'

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.now()
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
        now = datetime.now()
        expires_in = data['expires_in']
        expires = now + timedelta(seconds=expires_in)
        self.access_token = data['access_token']
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now 
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.now()
        if expires < now:
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
            print(r.status_code)
            print(r.json())
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



@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger = logging.getLogger(__name__)

@shared_task
def scrape_twitter():    
    # logger.info("ACTIVATED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    from home.models import Source, Article, NotificationMessage
    # assign the values accordingly
    consumer_key = 'XOoUFKNcJeHoSkGxkZUSraU4x'
    consumer_secret = '18fAwnwdZLqYDmkWzxuQwL8GalXguNskhnYv8dMPr8ZYhRez0y'
    access_token = '1510667747365109763-ak8OKMTG45Q5GW2HrNlGhJL5Oyss49'
    access_token_secret = "8NqJl5H97t6C11PdDYjksk5rHhVLpfiGsNcAZeMbNfviP"
    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)
    # calling the api 
    api = tweepy.API(auth)
    # fetching the statuses
    last_id = cache.get('last_id')
    if last_id:
        statuses = api.home_timeline(count=200, tweet_mode='extended', since_id=last_id)
    else:
        statuses = api.home_timeline(count=200, tweet_mode='extended')
    for status in statuses:
        if Article.objects.filter(external_id=status.id).exists():
            continue
        else:
            title = html.unescape(status.full_text)
            link = f'https://twitter.com/{status.user.screen_name}/status/{status.id}'
            pub_date = status.created_at
            if Source.objects.filter(external_id=status.user.id).exists():
                source = get_object_or_404(Source, external_id=status.user.id)
                external_id = status.id
                article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source, external_id=external_id)
                notifications_create(source, article)
            else:
                continue
        last_id = status.id
    cache.set('last_id', last_id)
    notification_messages = NotificationMessage.objects.all()
    for notification_message in notification_messages:
        if (datetime.now(timezone.utc) - notification_message.date) > timedelta(hours=24):
            notification_message.delete()


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(website=get_object_or_404(Website, name="Substack"))
    for source in substack_sources:
        feed_url = f'{source.url}feed'
        create_articles_from_feed(source, feed_url)
        time.sleep(30)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(website=get_object_or_404(Website, name="SeekingAlpha"))
    for source in seekingalpha_sources:
        feed_url = f'{source.url}.xml'
        create_articles_from_feed(source, feed_url)
        time.sleep(60)


@shared_task
def scrape_spotify():
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        episodes = spotify.get_episodes(source.external_id)
        episode_items = episodes['items']
        for episode_item in episode_items:
            title = episode_item['name']
            link = episode_item['external_urls']['spotify']
            if Article.objects.filter(title=title, link=link, source=source).exists():
                break
            else:
                article = Article.objects.create(title=episode_item['name'], link=episode_item['external_urls']['spotify'], pub_date=datetime.now(), source=source)
                notifications_create(source, article)
            
@shared_task
def scrape_youtube():
    api_key = "AIzaSyCJoe63T7VVTvIglkrE7OKZHfUxLMKuIuQ"
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    for source in youtube_sources:
        url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={source.external_id}&part=snippet,id&order=date&maxResults=20'
        r = requests.get(url)
        data = r.json()
        items = data['items']
        for item in items:
            title = item['snippet']['title']
            link = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            pub_date = item['snippet']['publishedAt']
            if Article.objects.filter(title=title, pub_date=pub_date, link=link, source=source).exists():
                break
            else:
                article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                notifications_create(source, article)