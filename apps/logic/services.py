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


def notifications_create(created_articles):
    from apps.home.models import Notification, NotificationMessage
    from apps.article.models import Article
    article_ids = [article.article_id for article in created_articles]
    articles = Article.objects.filter(article_id__in=article_ids)
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    keyword_notifications = notifications.filter(keyword__isnull=False)
    notifications_creation_list = []
    for keyword_notification in keyword_notifications:
        articles_with_keywords = articles.filter(title__search=keyword_notification.keyword)
        if articles_with_keywords.exists():
            for keyword_article in articles_with_keywords:
                if notification_messages.filter(article=keyword_article, notification__user=keyword_notification.user).exists() == False:
                    notifications_creation_list.append({"notification": keyword_notification, 'article': keyword_article, 'date': now()}) 
    for article in articles:
        if notifications.filter(source=article.source).exists():
            source_notifications = notifications.filter(source=article.source)
            for source_notification in source_notifications:
                if notification_messages.filter(article=article, notification__user=source_notification.user).exists() == False:
                    notifications_creation_list.append({"notification": source_notification, 'article': article, 'date': now()})
        lists_that_include_source = article.source.lists.all()
        for list in lists_that_include_source:
            if notifications.filter(list=list).exists():
                list_notifications = notifications.filter(list=list)
                for list_notification in list_notifications:
                    if notification_messages.filter(article=article, notification__user=list_notification.user).exists() == False:
                        notifications_creation_list.append({"notification": list_notification, 'article': article, 'date': now()})                   
    new_notification_messages = [
        NotificationMessage(
            notification=new_notification['notification'],
            article=new_notification['article'],
            date=new_notification['date'],
        )
        for new_notification in notifications_creation_list
    ]
    NotificationMessage.objects.bulk_create(new_notification_messages)


def single_notification_create(article):
    from apps.home.models import Notification, NotificationMessage
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    if notifications.filter(source=article.source).exists():
        source_notifications = notifications.filter(source=article.source)
        for source_notification in source_notifications:
            if notification_messages.filter(article=article, notification__user=source_notification.user).exists() == False:
                NotificationMessage.objects.create(notification=source_notification, article=article, date=now())
    lists_that_include_source = article.source.lists.all()
    for list in lists_that_include_source:
        if notifications.filter(list=list).exists():
            list_notifications = notifications.filter(list=list)
            for list_notification in list_notifications:
                if notification_messages.filter(article=article, notification__user=list_notification.user).exists() == False:
                    NotificationMessage.objects.create(notification=list_notification, article=article, date=now())


def create_articles_from_feed(source, feed_url, articles):
    from apps.article.models import Article
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
                if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                    break
                else:
                    created_article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                    single_notification_create(created_article)
            except:
                continue   
    except:
        pass


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