# Django imports
from itertools import count
from django.conf import settings
# Python imports
from urllib.request import Request, urlopen
import concurrent.futures
import os
import xml.etree.cElementTree as ET
import requests
from datetime import datetime, timedelta
import concurrent.futures
import tweepy

from accounts.models import Website
# Local imports


def file_creation_date_check(domain, sources):
    """Checks file creation date of xml files to see when sources were last scraped.
    If the last time was over 12 hours ago sources are scrapped again. The reason
    for this is to not allow to many requests to substacks (danger of IP-Ban)"""
    modification_date = datetime.fromtimestamp(
        os.path.getmtime(
            os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml')))
    if (datetime.now() - modification_date) > timedelta(hours=12):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(xml_scrape, sources)


def source_data_get(domain):
    """Goes through the scraped xml file and returns root (article data) and favicon"""
    data = ET.parse(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'))
    root = data.getroot()
    if os.path.isfile(
            os.path.join(settings.FAVICON_FILE_DIRECTORY,
                         f'{domain}.png')) == False:
        source_picture = root.find('.//url').text
        img_data = requests.get(source_picture).content
        with open(
                os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{domain}.png'),
                'wb') as handler:
            handler.write(img_data)
    favicon = f'home/favicons/{domain}.png'
    return root, favicon


def website_scrapping_initiate(source, domain):
    """Inititates web scrapping process. Returns True if sucessfull and False
    when a problem occured during the process."""
    try:
        xml_scrape(source, domain)
        _, _ = source_data_get(domain)
        return True
    except Exception:
        return False


def xml_scrape(source, domain):
    """Scrapes the xml feed of given source and writes it to a xml file on 
    local directory."""
    feed_url = f'{source}feed'
    req = Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
    website_data = urlopen(req)
    website_xml = website_data.read()
    website_data.close()
    with open(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'),
              'wb') as f:
        f.write(website_xml)


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
            domain = follow.screen_name
            name = follow.name
            external_id = follow.id
            import urllib.request
            urllib.request.urlretrieve(follow.profile_image_url_https.replace("_normal", ""), os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{domain}.png'))
            favicon_path = f'home/favicons/{domain}.png'
            Source.objects.create(url=url, domain=domain, name=name, favicon_path=favicon_path, paywall='No', website='Twitter', external_id=external_id)



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