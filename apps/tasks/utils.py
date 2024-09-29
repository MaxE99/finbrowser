import html
from urllib.request import Request, urlopen, urlretrieve
import xml.etree.ElementTree as ET
from time import sleep
from typing import Optional, List, Dict, Union
from io import BytesIO
import os

from PIL import Image
import boto3
from dateutil import parser

from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from apps.article.models import Article
from apps.source.models import Source
from apps.accounts.models import Website
from apps.home.models import Notification, NotificationMessage
from apps.article.models import Article

s3 = boto3.client("s3")


def create_source_profile_img(source, file_url: str):
    """
    Downloads an image from a given URL, resizes it, and uploads it to S3.

    Args:
        source (Source): The source object to update with the new favicon.
        file_url (str): The URL of the image to be downloaded.
    """
    urlretrieve(file_url, "temp_file.png")

    with Image.open("temp_file.png") as image:
        output = BytesIO()
        image = image.resize((175, 175))
        image.save(output, format="WEBP", quality=99)
        output.seek(0)

        s3.upload_fileobj(
            output,
            "finbrowser",
            os.path.join(settings.FAVICON_FILE_DIRECTORY, f"{source.slug}.webp"),
        )

    source.favicon_path = f"home/favicons/{source.slug}.webp"
    source.save()


def get_article_components(
    item, description: bool = False
) -> Dict[str, Union[str, timezone.datetime]]:
    """
    Extract components from an article item, including title, link, publication date,
    and optionally a description.

    Args:
        item: The XML element representing the article.
        description (bool): Whether to include the description in the output.

    Returns:
        Dict[str, Union[str, timezone.datetime]]: A dictionary containing the
        title, original title, link, and publication date.
    """

    def fully_unescape_string(title: str) -> str:
        """
        Unescape a double-escaped string.

        Args:
            title (str): The string to unescape.

        Returns:
            str: The unescaped string.
        """
        unescaped = ""
        while unescaped != title:
            title = html.unescape(title)
            unescaped = html.unescape(title)
        return title

    link = item.find(".//link").text
    date_string = item.find(".//pubDate").text
    parsed_date = parser.parse(date_string)

    pub_date = (
        parsed_date
        if timezone.is_aware(parsed_date)
        else timezone.make_aware(parsed_date, timezone=timezone.get_default_timezone())
    )
    title = fully_unescape_string(item.find(".//title").text)
    title_with_desc = None

    if description:
        description = fully_unescape_string(item.find(".//description").text)
        title_with_desc = f"{title}: {description}"[0:500]

    return {
        "title": title_with_desc,
        "original_title": title,
        "link": link,
        "pub_date": pub_date,
    }


def perform_article_status_check(
    creation_list: List[dict],
    articles,
    title: str,
    source: str,
    link: str,
    pub_date: Optional[timezone.datetime] = timezone.now(),
) -> Dict[str, List]:
    """
    Checks if an article already exists in the database. If it does,
    updates the article if there are changes. If not, appends the
    article details to the creation list.

    Args:
        creation_list (List[dict]): The list of articles to be created.
        articles (QuerySet): The queryset of existing articles.
        title (str): The title of the article.
        source (str): The source of the article.
        link (str): The link to the article.
        pub_date (Optional[timezone.datetime]): The publication date of the article.

    Returns:
        Dict[str, List]: A tuple containing the updated creation list
        and a boolean indicating if the article already exists.
    """
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

    if not article_exists:
        creation_list.append(
            {
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source,
            }
        )

    return {"creation_list": creation_list, "article_exists": article_exists}


def create_notifications(created_articles: List[Article]):
    """
    Creates notifications based on the articles that were created.

    Args:
        created_articles (List[Article]): A list of articles that were recently created.
    """

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


def bulk_create_articles_and_notifications(creation_list: List[Dict[str, str]]):
    """
    Bulk creates articles and their corresponding notifications.

    Args:
        creation_list (List[Dict[str, str]]): A list of article details to be created.
    """
    if creation_list:
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
        create_notifications(articles)


def create_articles_from_feed(source, feed_url: str, articles: models.QuerySet):
    """
    Creates articles from an RSS feed and generates notifications for them.

    Args:
        source (Source): The source of the articles.
        feed_url (str): The URL of the RSS feed.
        articles (QuerySet): The queryset of existing articles to check against.
    """
    create_article_list = []

    try:
        req = Request(
            feed_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
            },
        )
        with urlopen(req) as website_data:
            website_xml = website_data.read()

        items = ET.fromstring(website_xml).findall(".//item")
        for item in items:
            try:
                if str(source.website) in ["Substack", "Forbes"]:
                    components = get_article_components(item, description=True)
                    # in previous versions I didn't include the description in the title
                    if articles.filter(
                        title=components["originial_title"],
                        pub_date=components["pub_date"],
                        source=source,
                    ).exists():
                        break
                else:
                    components = get_article_components(item)

                title = html.unescape(title)
                lists = perform_article_status_check(
                    create_article_list,
                    articles,
                    title,
                    source,
                    components["link"],
                    pub_date=components["pub_date"],
                )
                create_article_list = lists["creation_list"]

                if lists["article_exists"]:
                    break

            except Exception as error:
                print(error)
                continue

    except Exception as error:
        print(error)

    bulk_create_articles_and_notifications(create_article_list)


def get_alt_feed_sources() -> List[Source]:
    """
    Retrieves a list of alternative feed sources.

    Returns:
        List[Source]: A queryset of sources with alternative feeds.
    """
    alt_feed_sources = (
        Source.objects.filter(website__name="Other", alt_feed__isnull=False)
        .exclude(alt_feed="none")
        .only("source_id", "alt_feed", "website")
    )
    return alt_feed_sources


def scrape_sources(
    source_name: str, extension: str, alt_feed: bool = False, timeout: int = 0
):
    """
    Scrapes articles from specified sources based on the source name and feed type.

    Args:
        source_name (str): The name of the source website.
        extension (str): The extension to append to the source URL.
        alt_feed (bool): Flag to indicate if alternative feeds should be used.
        timeout (int): The number of seconds to wait between requests.
    """
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
        feed_url = source.alt_feed if source.alt_feed else f"{source.url}{extension}"

        try:
            create_articles_from_feed(source, feed_url, articles)
            if timeout:
                sleep(timeout)
        except Exception as error:
            print(f"Scrapping {source} failed due to this error: {error}")


def get_youtube_sources_and_articles() -> Dict[str, models.QuerySet]:
    """
    Retrieves YouTube sources and their associated articles.

    Returns:
        Dict[str, models.QuerySet]: A tuple containing a list of YouTube sources and their articles.
    """
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=youtube_sources).only(
        "title", "pub_date", "link", "source"
    )
    return {"sources": youtube_sources, "articles": articles}


def get_spotify_sources_and_articles() -> Dict[str, models.QuerySet]:
    """
    Retrieves Spotify sources and their associated articles.

    Returns:
        Dict[str, models.QuerySet]: A tuple containing a list of Spotify sources and their articles.
    """
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=spotify_sources).only(
        "title", "link", "source"
    )
    return {"sources": spotify_sources, "articles": articles}
