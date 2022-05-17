# Python import
from datetime import datetime
from operator import itemgetter

from django.shortcuts import get_object_or_404
from pytz import timezone


class Article(object):

    def __init__(self, picture, title, link, pub_date):
        self.picture = picture
        self.title = title
        self.link = link
        self.pub_date = pub_date


def article_create(articles, favicon, title, link, pub_date):
    """Creates new article and appends it to list of articles."""
    new_article_instance = globals()['Article']
    instance = new_article_instance(favicon, title, link, pub_date)
    articles.append(instance)


def main_website_source_set(instance):
    """If more than 50% of sources come from one website field main_website_source is set to this website"""
    websites = [["Medium", 0], ["Other", 0], ["SeekingAlpha", 0],
                ["Substack", 0], ["Twitter", 0], ["YouTube", 0]]
    for source in instance.sources.all():
        for website in websites:
            if source.website == website[0]:
                website[1] += 1
                break
    websites = sorted(websites, key=itemgetter(1), reverse=True)
    if not instance.sources.all() or (websites[0][1] /
                                      len(instance.sources.all())) * 100 <= 50:
        instance.main_website_source = ''
    else:
        instance.main_website_source = websites[0][0]
    return instance


def notifications_create(source, article):
    from home.models import Notification, NotificationMessage
    source_notifications = Notification.objects.filter(source=source)
    for source_notification in source_notifications:
        NotificationMessage.objects.create(notification=source_notification, article=article)
    sources_in_lists = source.lists.all()
    for list in sources_in_lists:
        if Notification.objects.filter(list=list).exists():
            list_notifications = Notification.objects.filter(list=list)
            for list_notification in list_notifications:
                NotificationMessage.objects.create(notification=list_notification, article=article)