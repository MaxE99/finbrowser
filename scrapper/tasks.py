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
import requests
# Local imports
from home.logic.services import notifications_create, create_articles_from_feed
from home.logic.scrapper import SpotifyAPI
from home.models import Article, Source
from accounts.models import Website


# @after_setup_logger.connect
# def setup_loggers(logger, *args, **kwargs):
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#     # add filehandler
#     fh = logging.FileHandler('logs.log')
#     fh.setLevel(logging.DEBUG)
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)

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
    client_id = 'b0b3c71663ef4c7bb1bcac4cfb1a0a78'
    client_secret = '7096cbb406474c42a2357500356f3663'
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
    api_key = "AIzaSyAAz_6R_6g64KbC8xQscbeiArA0OOX2uso"
    youtube_sources = Source.objects.filter(website=get_object_or_404(Website, name="YouTube"))
    for source in youtube_sources:
        url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={source.external_id}&part=snippet,id&order=date&maxResults=20'
        r = requests.get(url)
        data = r.json()
        try:
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
        except:
            logger.info("Error!!!")
            logger.info(source)
            logger.info(url)
            logger.info(data)

