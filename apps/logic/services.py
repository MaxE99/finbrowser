# Django import
from django.utils.timezone import now
# Python import
from urllib.request import Request, urlopen
import xml.etree.cElementTree as ET
import html
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


def notifications_create(articles):
    from apps.home.models import Notification, NotificationMessage
    notifications = Notification.objects.all()
    notification_messages = NotificationMessage.objects.all().select_related("notification__user")
    notifications_creation_list = []
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
                        notifications_creation_list.append({"notification": source_notification, 'article': article, 'date': now()})
    new_notification_messages = [
        NotificationMessage(
            notification=new_notification['notification'],
            article=new_notification['article'],
            date=new_notification['date'],
        )
        for new_notification in notifications_creation_list
    ]
    NotificationMessage.objects.bulk_create(new_notification_messages)


def create_articles_from_feed(source, feed_url, articles):
    from apps.article.models import Article
    req = Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
    website_data = urlopen(req)
    website_xml = website_data.read()
    website_data.close()
    root = ET.fromstring(website_xml)
    for item in root.findall('.//item'):
        try:
            title, link, pub_date = article_components_get(item)
            title = html.unescape(title)
            if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                articles = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                notifications_create(articles)
        except:
            continue   