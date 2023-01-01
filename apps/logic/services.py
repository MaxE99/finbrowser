# Django import
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Q
# Python import
import tweepy
from urllib.request import Request, urlopen
import xml.etree.cElementTree as ET
import html
from io import BytesIO
from PIL import Image
import urllib.request
import os
import boto3
import re
# Local import
from apps.logic.selectors import article_components_get


def main_website_source_set(instance):
    """If more than 50% of sources come from one website field main_website_source is set to this website"""
    websites = {'Other': 0, 'SeekingAlpha':0, 'Spotify':0, 'Substack':0, 'Twitter':0, 'YouTube':0}
    list_sources = instance.sources.all()
    for source in list_sources:
        if str(source.website) in websites:
            websites[str(source.website)] += 1
    top_list_source = max(websites, key=websites.get)
    if not instance.sources.all() or (websites[top_list_source]/list_sources.count()) * 100 <= 50:
        instance.main_website_source = ''
    else:
        instance.main_website_source = top_list_source
    return instance


def notifications_create(created_articles):
    from apps.home.models import Notification, NotificationMessage
    from apps.article.models import Article
    notifications_creation_list = []
    notifications = Notification.objects.all()
    source_notifications = notifications.filter(source__isnull=False)
    articles = Article.objects.filter(article_id__in=[article.article_id for article in created_articles])
    for notification in notifications.exclude(source__isnull=False).select_related("stock"):
        if notification.keyword:
            for article in articles.filter(search_vector=notification.keyword).iterator():
                notifications_creation_list.append({"notification": notification, 'article': article, 'date': now(), 'user': notification.user})
        else:
            for article in articles.filter(Q(search_vector=notification.stock.ticker) | Q(search_vector=notification.stock.short_company_name)).iterator():
                notifications_creation_list.append({"notification": notification, 'article': article, 'date': now(), 'user': notification.user})
    for article in articles:
        for notification in source_notifications.filter(source=article.source).iterator():
            notifications_creation_list.append({"notification": notification, 'article': article, 'date': now(), 'user': notification.user})
    existing_dicts = set()
    filtered_list = []
    for d in notifications_creation_list:
        if (d['article'], d['user']) not in existing_dicts:
            existing_dicts.add((d['article'], d['user']))
            filtered_list.append(d)
    new_notification_messages = [
        NotificationMessage(
            notification=new_notification['notification'],
            article=new_notification['article'],
            date=new_notification['date'],
        )
        for new_notification in filtered_list
    ]
    NotificationMessage.objects.bulk_create(new_notification_messages)


def bulk_create_articles_and_notifications(creation_list):
    from apps.article.models import Article
    if len(creation_list) > 0:
        new_articles = [
            Article(
                title=article_new['title'],
                link=article_new['link'],
                pub_date=article_new['pub_date'],
                source=article_new['source'],
            )
            for article_new in creation_list
        ]
        articles = Article.objects.bulk_create(new_articles)
        notifications_create(articles)


def create_articles_from_feed(source, feed_url, articles):
    create_article_list = []
    try:
        req = Request(feed_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"})
        website_data = urlopen(req)
        website_xml = website_data.read()
        website_data.close()
        items = ET.fromstring(website_xml).findall('.//item')
        for item in items:
            try:
                title, link, pub_date = article_components_get(item)
                title = html.unescape(title)
                if articles.filter(title=title, pub_date=pub_date, source=source).exists():
                    break
                else:
                    create_article_list.append({'title': title, 'link': link, 'pub_date': pub_date, 'source': source})
            except:
                continue   
    except:
        pass
    bulk_create_articles_and_notifications(create_article_list)


s3 = boto3.client('s3')

def source_profile_img_create(source, file_url):
        urllib.request.urlretrieve(file_url, 'temp_file.png')
        im = Image.open('temp_file.png')
        output = BytesIO()
        im = im.resize((175, 175))
        im.save(output, format='WEBP', quality=99)
        output.seek(0)
        s3.upload_fileobj(output, 'finbrowser', os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{source.slug}.webp'))
        source.favicon_path = f'home/favicons/{source.slug}.webp'
        source.save()


def tweet_img_upload(tweet_type, file_url):
        urllib.request.urlretrieve(file_url, 'temp_file.png')
        im = Image.open('temp_file.png')
        output = BytesIO()
        im.save(output, format='WEBP', quality=99)
        output.seek(0)
        s3.upload_fileobj(output, 'finbrowser', os.path.join(settings.TWEET_IMG_FILE_DIRECTORY, f'tweet_img_{tweet_type.tweet_type_id}.webp'), ExtraArgs={'Metadata': {'Content-Type': 'image/webp'}})
        tweet_type.image_path = f'home/tweet_imgs/tweet_img_{tweet_type.tweet_type_id}.webp'
        return tweet_type


def initial_tweet_img_path_upload(tweet_type, file_url):
        urllib.request.urlretrieve(file_url, 'temp_file.png')
        im = Image.open('temp_file.png')
        output = BytesIO()
        im.save(output, format='WEBP', quality=99)
        output.seek(0)
        s3.upload_fileobj(output, 'finbrowser', os.path.join(settings.INITIAL_TWEET_IMG_FILE_DIRECTORY, f'initial_tweet_img_{tweet_type.tweet_type_id}.webp'))
        tweet_type.initial_tweet_img_path = f'home/initial_tweet_imgs/initial_tweet_img_{tweet_type.tweet_type_id}.webp'
        return tweet_type


def twitter_create_api_settings():
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)  


def tweet_type_create(status, twitter_user_id, api):
    from apps.article.models import TweetType
    tweet_type = TweetType.objects.create(type = "Basic")
    if 'media' in status.entities:
        if 'media_url_https' in status.entities['media'][0]:
            tweet_type.type = "Image"
            tweet_type = tweet_img_upload(tweet_type, status.entities['media'][0]['media_url_https'])
    elif len(status.entities['urls']) > 0:
        if 'expanded_url' in status.entities['urls'][0]:
            # title = html.unescape(status.full_text) # With links I don't escape the title
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
    return tweet_type
    # return title, tweet_type

# def change_format_of_pngs_and_upload_them_as_wepbs_from_dev():
#     images = glob.glob("test_imgs/*.png")
#     for image in images:
#         if image.endswith(".png"):
#             with open(image, 'rb') as file:
#                 im = Image.open(file)
#                 output = BytesIO()
#                 im = im.resize((175, 175))
#                 im.save(output, format='WEBP', quality=99)
#                 output.seek(0)
#                 s3.upload_fileobj(output, 'finbrowser', os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{image.replace(".png", "").replace("test_imgs/", "")}.webp'))