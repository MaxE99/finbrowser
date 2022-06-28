# Django imports
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
# Python imports
import os
import requests
from datetime import timedelta
import tweepy
import base64
import urllib.request
# Local imports
from apps.home.models import Source
from apps.accounts.models import Website

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


def spotify_get_profile_images():
    client_id = 'b0b3c71663ef4c7bb1bcac4cfb1a0a78'
    client_secret = '7096cbb406474c42a2357500356f3663'
    spotify_sources = Source.objects.filter(website=get_object_or_404(Website, name="Spotify"))
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        podcaster = spotify.get_podcaster(source.external_id)
        urllib.request.urlretrieve(podcaster['images'][0]['url'], os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{source.slug}.png'))
        favicon_path = f'home/favicons/{source.slug}.png'
        source.favicon_path = favicon_path
        source.save()


def twitter_scrape_followings():
    from home.models import Source
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
    followings = api.get_friends(count=71)
    for follow in followings:
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        else:
            url = f'https://twitter.com/{follow.screen_name}'
            slug = follow.screen_name
            name = follow.name
            external_id = follow.id
            urllib.request.urlretrieve(follow.profile_image_url_https.replace("_normal", ""), os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{slug}.png'))
            favicon_path = f'home/favicons/{slug}.png'
            Source.objects.create(url=url, slug=slug, name=name, favicon_path=favicon_path, paywall='No', website='Twitter', external_id=external_id)


def youtube_get_profile_images():
    api_key = "AIzaSyAAz_6R_6g64KbC8xQscbeiArA0OOX2uso"
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

