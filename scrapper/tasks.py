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
# Local imports
from home.logic.services import notifications_create

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




