from __future__ import absolute_import, unicode_literals

from celery import shared_task

import tweepy

@shared_task
def add(x,y):
    return x+y

@shared_task
def scrape_twitter():    
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
    statuses = api.home_timeline(count=1, tweet_mode='extended')
    # printing the screen names of each status
    for status in statuses:
        user_name = status.user.name
        user_id = status.user.id
        text = status.full_text
        creation_date = status.created_at
        tweet_link = f'https://twitter.com/{status.user.screen_name}/status/{status.id}'
        return user_name
