# Python import
import html
import os
import re
from urllib.request import Request, urlopen
import urllib.request

import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
import boto3
import tweepy

# Django import
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


# Local import
from apps.logic.selectors import article_components_get
from apps.accounts.forms import (
    EmailAndUsernameChangeForm,
    PasswordChangingForm,
    TimezoneChangeForm,
)


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
    return creation_list


def handle_settings_actions(request):
    if "changeProfileForm" in request.POST:
        email_and_name_change_form = EmailAndUsernameChangeForm(
            request.POST,
            username=request.user.username,
            email=request.user.email,
            instance=request.user,
        )
        change_timezone_form = TimezoneChangeForm(
            request.POST, instance=request.user.profile
        )

        if change_timezone_form.is_valid():
            change_timezone_form.save()
            request.session["django_timezone"] = request.POST["timezone"]
        if email_and_name_change_form.is_valid():
            request.user.save()
            request.user.profile.save()
            messages.success(request, "Profile has been updated!")
        else:
            messages.error(request, "Error: Username or email already exists!")
    elif "changePasswordForm" in request.POST:
        change_password_form = PasswordChangingForm(
            user=request.user, data=request.POST or None
        )
        if change_password_form.is_valid():
            change_password_form.save()
            update_session_auth_hash(request, change_password_form.user)
            messages.success(request, "Password has been changed!")
        else:
            messages.error(request, "New password is invalid!")


def notifications_create(created_articles):
    from apps.home.models import Notification, NotificationMessage
    from apps.article.models import Article

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
                link=article_new["link"],
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"
            },
        )
        website_data = urlopen(req)
        website_xml = website_data.read()
        website_data.close()
        items = ET.fromstring(website_xml).findall(".//item")
        for item in items:
            try:
                if source.website == "Substack":
                    title, originial_title, link, pub_date = article_components_get(
                        item, True
                    )
                    # in previous versions I didn't include the description in the title
                    if articles.filter(
                        title=originial_title, pub_date=pub_date, source=source
                    ).exists():
                        break
                else:
                    _, title, link, pub_date = article_components_get(item)
                title = html.unescape(title)
                create_article_list = article_creation_check(
                    create_article_list,
                    articles,
                    title,
                    source,
                    link,
                    pub_date=pub_date,
                )
            except Exception as _:
                continue
    except Exception as _:
        pass
    bulk_create_articles_and_notifications(create_article_list)


s3 = boto3.client("s3")


def source_profile_img_create(source, file_url):
    urllib.request.urlretrieve(file_url, "temp_file.png")
    image = Image.open("temp_file.png")
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


def tweet_img_upload(tweet_type, file_url):
    urllib.request.urlretrieve(file_url, "temp_file.png")
    image = Image.open("temp_file.png")
    output = BytesIO()
    image.save(output, format="WEBP", quality=99)
    output.seek(0)
    s3.upload_fileobj(
        output,
        "finbrowser",
        os.path.join(
            settings.TWEET_IMG_FILE_DIRECTORY,
            f"tweet_img_{tweet_type.tweet_type_id}.webp",
        ),
        ExtraArgs={"Metadata": {"Content-Type": "image/webp"}},
    )
    tweet_type.image_path = f"home/tweet_imgs/tweet_img_{tweet_type.tweet_type_id}.webp"
    return tweet_type


def initial_tweet_img_path_upload(tweet_type, file_url):
    urllib.request.urlretrieve(file_url, "temp_file.png")
    image = Image.open("temp_file.png")
    output = BytesIO()
    image.save(output, format="WEBP", quality=99)
    output.seek(0)
    s3.upload_fileobj(
        output,
        "finbrowser",
        os.path.join(
            settings.INITIAL_TWEET_IMG_FILE_DIRECTORY,
            f"initial_tweet_img_{tweet_type.tweet_type_id}.webp",
        ),
    )
    tweet_type.initial_tweet_img_path = (
        f"home/initial_tweet_imgs/initial_tweet_img_{tweet_type.tweet_type_id}.webp"
    )
    return tweet_type


def twitter_create_api_settings():
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def tweet_type_create(status, twitter_user_id, api):
    from apps.article.models import TweetType

    tweet_type = TweetType.objects.create(type="Basic")
    if "media" in status.entities:
        if "media_url_https" in status.entities["media"][0]:
            tweet_type.type = "Image"
            tweet_type = tweet_img_upload(
                tweet_type, status.entities["media"][0]["media_url_https"]
            )
    elif len(status.entities["urls"]) > 0:
        if "expanded_url" in status.entities["urls"][0]:
            # title = html.unescape(status.full_text) # With links I don't escape the title
            tweet_type.type = "Link"
            tweet_type.link = status.entities["urls"][0]["expanded_url"]
    in_reply_to_user_id = status.in_reply_to_user_id
    if hasattr(status, "retweeted_status"):
        tweet_type.pub_date = status.retweeted_status.created_at
        tweet_type.text = re.sub(
            r"http\S+", "", html.unescape(status.retweeted_status.full_text)
        )
        tweet_type.author = status.retweeted_status.user.name
        if "media" in status.retweeted_status._json["entities"]:
            if (
                "media_url_https"
                in status.retweeted_status._json["entities"]["media"][0]
            ):
                tweet_type.image_path = None  # Despite the status being a retweet Twitter sometimes sends a picture in the media dictionary which would lead to the image being shown 2 times
                tweet_type = initial_tweet_img_path_upload(
                    tweet_type,
                    status.retweeted_status._json["entities"]["media"][0][
                        "media_url_https"
                    ],
                )
        tweet_type.type = "Retweet"
    elif in_reply_to_user_id is not None and in_reply_to_user_id != twitter_user_id:
        tweet_reply_id = status.in_reply_to_status_id
        tweet_reply_info = api.get_status(id=tweet_reply_id, tweet_mode="extended")
        tweet_type.pub_date = tweet_reply_info.created_at
        tweet_type.text = re.sub(
            r"http\S+", "", html.unescape(tweet_reply_info.full_text)
        )
        tweet_type.author = tweet_reply_info.user.name
        if hasattr(tweet_reply_info.entities, "media"):
            if "media_url_https" in tweet_reply_info.entities["media"][0]:
                tweet_type = initial_tweet_img_path_upload(
                    tweet_type, tweet_reply_info.entities["media"][0]["media_url_https"]
                )
        tweet_type.type = "Reply"
    elif status.is_quote_status:
        tweet_type.pub_date = status.quoted_status.created_at
        tweet_type.text = re.sub(
            r"http\S+", "", html.unescape(status.quoted_status.full_text)
        )
        tweet_type.author = status.quoted_status.user.name
        if "media" in status.quoted_status._json["entities"]:
            if "media_url_https" in status.quoted_status._json["entities"]["media"][0]:
                tweet_type = initial_tweet_img_path_upload(
                    tweet_type,
                    status.quoted_status._json["entities"]["media"][0][
                        "media_url_https"
                    ],
                )
        tweet_type.type = "Quote"
    tweet_type.save()
    return tweet_type
    # return title, tweet_type


# =================================================================================
# Functions that need to be used from time to time
# =================================================================================

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
