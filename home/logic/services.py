# Python import
from datetime import datetime
from operator import itemgetter
from urllib.request import Request, urlopen
import xml.etree.cElementTree as ET
# Local import
from home.logic.selectors import article_components_get

class Article(object):

    def __init__(self, picture, title, link, pub_date):
        self.picture = picture
        self.title = title
        self.link = link
        self.pub_date = pub_date


# def article_create(articles, favicon, title, link, pub_date):
#     """Creates new article and appends it to list of articles."""
#     new_article_instance = globals()['Article']
#     instance = new_article_instance(favicon, title, link, pub_date)
#     articles.append(instance)


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


def notifications_create(source, article):
    from home.models import Notification, NotificationMessage
    if Notification.objects.filter(source=source).exists():
        source_notifications = Notification.objects.filter(source=source)
        for source_notification in source_notifications:
            if NotificationMessage.objects.filter(article=article, notification__user=source_notification.user).exists():
                continue
            else:
                NotificationMessage.objects.create(notification=source_notification, article=article, date=datetime.now())
    lists_that_include_source = source.lists.all()
    for list in lists_that_include_source:
        if Notification.objects.filter(list=list).exists():
            list_notifications = Notification.objects.filter(list=list)
            for list_notification in list_notifications:
                if NotificationMessage.objects.filter(article=article, notification__user=list_notification.user).exists():
                    continue
                else:
                    NotificationMessage.objects.create(notification=list_notification, article=article, date=datetime.now())


def create_articles_from_feed(source, feed_url):
    from home.models import Article
    req = Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
    website_data = urlopen(req)
    website_xml = website_data.read()
    website_data.close()
    root = ET.fromstring(website_xml)
    for item in root.findall('.//item'):
        try:
            title, link, pub_date = article_components_get(item)
            if Article.objects.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                notifications_create(source, article)
        except:
            continue   