# Django imports
from django.conf import settings
from django.shortcuts import get_object_or_404
# Python imports
import os
import requests
from datetime import datetime, timedelta
import tweepy
import base64
import urllib.request
# Local imports
from home.models import Source
from accounts.models import Website

# def file_creation_date_check(domain, sources):
#     """Checks file creation date of xml files to see when sources were last scraped.
#     If the last time was over 12 hours ago sources are scrapped again. The reason
#     for this is to not allow to many requests to substacks (danger of IP-Ban)"""
#     modification_date = datetime.fromtimestamp(
#         os.path.getmtime(
#             os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml')))
#     if (datetime.now() - modification_date) > timedelta(hours=12):
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             executor.map(xml_scrape, sources)


# def source_data_get(domain):
#     """Goes through the scraped xml file and returns root (article data) and favicon"""
#     data = ET.parse(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'))
#     root = data.getroot()
#     if os.path.isfile(
#             os.path.join(settings.FAVICON_FILE_DIRECTORY,
#                          f'{domain}.png')) == False:
#         source_picture = root.find('.//url').text
#         img_data = requests.get(source_picture).content
#         with open(
#                 os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{domain}.png'),
#                 'wb') as handler:
#             handler.write(img_data)
#     favicon = f'home/favicons/{domain}.png'
#     return root, favicon


# def website_scrapping_initiate(source, domain):
#     """Inititates web scrapping process. Returns True if sucessfull and False
#     when a problem occured during the process."""
#     try:
#         xml_scrape(source, domain)
#         _, _ = source_data_get(domain)
#         return True
#     except Exception:
#         return False


# def xml_scrape(source, domain):
#     """Scrapes the xml feed of given source and writes it to a xml file on 
#     local directory."""
#     feed_url = f'{source}feed'
#     req = Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
#     website_data = urlopen(req)
#     website_xml = website_data.read()
#     website_data.close()
#     with open(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'),
#               'wb') as f:
#         f.write(website_xml)





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


# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# import html

# def article_components_get(item):
#     """Goes through xml item and returns title, link and publishing date of article."""

#     # some titles in the xml files have been escaped twice which makes it necesseary to ecape the titles more than once
#     def double_escaped_string_unescape(title):
#         unescaped = ""
#         while unescaped != title:
#             title = html.unescape(title)
#             unescaped = html.unescape(title)
#         return title

#     title = double_escaped_string_unescape(item.find('.//title').text)
#     link = item.find('.//link').text
#     pub_date = item.find('.//pubDate').text[:-4]
#     pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %X')
#     return title, link, pub_date

# def articles_search():
#     from home.models import Source, Article
#     sources = Source.objects.all()
#     for source in sources:
#         root, _ = source_data_get(source)
#         for item in root.findall('.//item'):
#             try:
#                 title, link, pub_date = article_components_get(item)
#                 Article.objects.create(title=title,
#                                        link=link,
#                                        pub_date=pub_date,
#                                        source=source)
#             except Exception as e:
#                 print(e)

# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface
# Refactor this later this is just to get articles to work on my interface