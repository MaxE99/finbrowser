# Django import
from django.utils.timezone import now
from django.conf import settings
# Python import
from urllib.request import Request, urlopen
import xml.etree.cElementTree as ET
import html
from io import BytesIO
from PIL import Image
import urllib.request
import os
import boto3
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


def notification_double_prevention(notification_messages, notifications_creation_list, article, notification):
    notification_created = False
    for d in notifications_creation_list:
        if d['notification'].user == notification.user and d['article'] == article:
            notification_created = True
            break
    if notification_messages.filter(article=article, notification__user=notification.user).exists() == False and notification_created == False:
        notifications_creation_list.append({"notification": notification, 'article': article, 'date': now()}) 


def notifications_create(created_articles):
    from apps.home.models import Notification, NotificationMessage
    from apps.article.models import Article
    articles = Article.objects.filter(article_id__in=[article.article_id for article in created_articles])
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    keyword_notifications = notifications.filter(keyword__isnull=False)
    notifications_creation_list = []
    for keyword_notification in keyword_notifications:
        articles_with_keywords = articles.filter(title__search=keyword_notification.keyword)
        if articles_with_keywords.exists():
            for keyword_article in articles_with_keywords:
                notification_double_prevention(notification_messages, notifications_creation_list, keyword_article, keyword_notification)
    for article in articles:
        if notifications.filter(source=article.source).exists():
            source_notifications = notifications.filter(source=article.source)
            for source_notification in source_notifications:
                notification_double_prevention(notification_messages, notifications_creation_list, article, source_notification)
        lists_that_include_source = article.source.lists.all()
        for list in lists_that_include_source:
            if notifications.filter(list=list).exists():
                list_notifications = notifications.filter(list=list)
                for list_notification in list_notifications:
                    notification_double_prevention(notification_messages, notifications_creation_list, article, list_notification)                 
    new_notification_messages = [
        NotificationMessage(
            notification=new_notification['notification'],
            article=new_notification['article'],
            date=new_notification['date'],
        )
        for new_notification in notifications_creation_list
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
        s3.upload_fileobj(output, 'finbrowser', os.path.join(settings.TWEET_IMG_FILE_DIRECTORY, f'tweet_img_{tweet_type.tweet_type_id}.webp'))
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