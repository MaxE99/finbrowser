# Standard import
import html
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from time import sleep

# External imports
from dateutil import parser

# Django import
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

# local imports
from apps.article.models import Article
from apps.source.models import Source
from apps.accounts.models import Website
from apps.home.models import Notification, NotificationMessage


def article_components_get(item, description=False):
    """Goes through xml item and returns title, link and publishing date of article."""

    # some titles in the xml files have been escaped twice which makes it necesseary to ecape the titles more than once
    def double_escaped_string_unescape(title):
        unescaped = ""
        while unescaped != title:
            title = html.unescape(title)
            unescaped = html.unescape(title)
        return title

    link = item.find(".//link").text

    date_string = item.find(".//pubDate").text
    parsed_date = parser.parse(date_string)
    if timezone.is_aware(parsed_date):
        pub_date = parsed_date
    else:
        pub_date = timezone.make_aware(
            parsed_date, timezone=timezone.get_default_timezone()
        )
    title = double_escaped_string_unescape(item.find(".//title").text)
    if description:
        description = double_escaped_string_unescape(item.find(".//description").text)
        title_with_desc = f"{title}: {description}"[0:500]
        return title_with_desc, title, link, pub_date
    return None, title, link, pub_date


def article_creation_check(
    creation_list, articles, title, source, link, pub_date=timezone.now()
):
    """Checks if article already exists and if so if changed need to be made. Otherwise appends to creation list"""
    article_exists = False
    if articles.filter(link=link, source=source).exists():
        article = articles.filter(link=link, source=source).first()
        if article.title != title:
            article.title = title
            article.pub_date = pub_date
            article.save()
        article_exists = True
    elif articles.filter(title=title, source=source).exists():
        article = articles.filter(title=title, source=source).first()
        if article.link != link:
            article.link = link
            article.pub_date = pub_date
            article.save()
        article_exists = True
    if article_exists is False:
        creation_list.append(
            {
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source,
            }
        )
    return creation_list, article_exists


def notifications_create(created_articles):
    notifications_creation_list = []
    notifications = Notification.objects.all()
    source_notifications = notifications.filter(source__isnull=False)
    articles = Article.objects.filter(
        article_id__in=[article.article_id for article in created_articles]
    )
    for notification in notifications.exclude(source__isnull=False).select_related(
        "stock"
    ):
        if notification.keyword:
            for article in articles.filter(
                search_vector=notification.keyword
            ).iterator():
                notifications_creation_list.append(
                    {
                        "notification": notification,
                        "article": article,
                        "date": timezone.now(),
                        "user": notification.user,
                    }
                )
        else:
            for article in articles.filter(
                Q(search_vector=notification.stock.ticker)
                | Q(search_vector=notification.stock.short_company_name)
            ).iterator():
                notifications_creation_list.append(
                    {
                        "notification": notification,
                        "article": article,
                        "date": timezone.now(),
                        "user": notification.user,
                    }
                )
    for article in articles:
        for notification in source_notifications.filter(
            source=article.source
        ).iterator():
            notifications_creation_list.append(
                {
                    "notification": notification,
                    "article": article,
                    "date": timezone.now(),
                    "user": notification.user,
                }
            )
    existing_dicts = set()
    filtered_list = []
    for ncl_dict in notifications_creation_list:
        if (ncl_dict["article"], ncl_dict["user"]) not in existing_dicts:
            existing_dicts.add((ncl_dict["article"], ncl_dict["user"]))
            filtered_list.append(ncl_dict)
    new_notification_messages = [
        NotificationMessage(
            notification=new_notification["notification"],
            article=new_notification["article"],
            date=new_notification["date"],
        )
        for new_notification in filtered_list
    ]
    NotificationMessage.objects.bulk_create(new_notification_messages)


def bulk_create_articles_and_notifications(creation_list):
    from apps.article.models import Article

    if len(creation_list):
        new_articles = [
            Article(
                title=article_new["title"][:500],
                link=article_new["link"][:500],
                pub_date=article_new["pub_date"],
                source=article_new["source"],
            )
            for article_new in creation_list
        ]
        articles = Article.objects.bulk_create(new_articles)
        notifications_create(articles)


def create_articles_from_feed(source, feed_url, articles):
    create_article_list = []
    try:
        req = Request(
            feed_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
            },
        )
        website_data = urlopen(req)
        website_xml = website_data.read()
        website_data.close()
        items = ET.fromstring(website_xml).findall(".//item")
        for item in items:
            try:
                if str(source.website) in ["Substack", "Forbes"]:
                    title, originial_title, link, pub_date = article_components_get(
                        item, description=True
                    )
                    # in previous versions I didn't include the description in the title
                    if articles.filter(
                        title=originial_title, pub_date=pub_date, source=source
                    ).exists():
                        break
                else:
                    _, title, link, pub_date = article_components_get(item)
                title = html.unescape(title)
                create_article_list, article_exists = article_creation_check(
                    create_article_list,
                    articles,
                    title,
                    source,
                    link,
                    pub_date=pub_date,
                )
                if article_exists:
                    break
            except Exception as error:
                print(error)
                continue
    except Exception as error:
        print(error)
        pass
    bulk_create_articles_and_notifications(create_article_list)


##################################################################


def get_alt_feed_sources():
    alt_feed_sources = (
        Source.objects.filter(website__name="Other", alt_feed__isnull=False)
        .exclude(alt_feed="none")
        .only("source_id", "alt_feed", "website")
    )
    return alt_feed_sources


def scrape_sources(source_name, extension, alt_feed=False, timeout=0):
    if alt_feed:
        sources = get_alt_feed_sources()
    else:
        sources = Source.objects.filter(
            website=get_object_or_404(Website, name=source_name)
        ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in sources:
        if source.alt_feed:
            feed_url = source.alt_feed
        else:
            feed_url = f"{source.url}{extension}"
        try:
            create_articles_from_feed(source, feed_url, articles)
            if timeout:
                sleep(timeout)
        except Exception as error:
            print(f"Scrapping {source} failed due to this error: {error}")
            continue


def get_youtube_sources_and_articles():
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=youtube_sources).only(
        "title", "pub_date", "link", "source"
    )
    return youtube_sources, articles


def get_spotify_sources_and_articles():
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=spotify_sources).only(
        "title", "link", "source"
    )
    return spotify_sources, articles
