from __future__ import absolute_import, unicode_literals

# Python imports
from datetime import timedelta
from html import unescape
from time import sleep
from base64 import b64encode
from os import environ
from re import sub as re_sub
from celery import shared_task
from requests import post as request_post
from requests import get as request_get
from boto3 import client


# Django imports
from django.core.cache import cache
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


# Local imports
from apps.logic.services import (
    bulk_create_articles_and_notifications,
    notifications_create,
    create_articles_from_feed,
    source_profile_img_create,
    twitter_create_api_settings,
    tweet_type_create,
    article_creation_check,
)
from apps.article.models import Article, TweetType
from apps.home.models import NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source


User = get_user_model()

s3 = client("s3")


class SpotifyAPI(object):
    access_token = None
    access_token_expires = timezone.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credientals(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credientals()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        request = request_post(
            self.token_url,
            data=self.get_token_data(),
            headers=self.get_token_headers(),
            timeout=10,
        )
        if request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        data = request.json()
        expires_in = data["expires_in"]
        expires = timezone.now() + timedelta(seconds=expires_in)
        self.access_token = data["access_token"]
        self.access_token_expires = expires
        self.access_token_did_expire = expires < timezone.now()
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        if expires < timezone.now():
            self.perform_auth()
            return self.get_access_token()
        if token is None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_episodes(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        request = request_get(lookup_url, headers=headers, timeout=10)
        if request.status_code not in range(200, 299):
            return {}
        return request.json()

    def get_podcaster(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        r = request_get(lookup_url, headers=headers, timeout=10)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()


@shared_task
def scrape_twitter():
    api = twitter_create_api_settings()
    last_id = cache.get("last_id")
    if last_id:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", since_id=last_id, include_entities=True
        )
    else:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", include_entities=True
        )
    existing_tweets = Article.objects.filter(external_id__isnull=False).values_list(
        "external_id", flat=True
    )
    sources = Source.objects.all().only("source_id", "external_id")
    tweet_creation_list = []
    for status in statuses:
        try:
            tweet_external_id = status.id
            if str(tweet_external_id) not in existing_tweets:
                twitter_user_id = status.user.id
                if sources.filter(external_id=twitter_user_id).exists():
                    title = re_sub(r"http\S+", "", unescape(status.full_text))
                    if not title.strip():
                        continue
                    link = f"https://twitter.com/{status.user.screen_name}/status/{tweet_external_id}"
                    pub_date = status.created_at
                    # title, tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_creation_list.append(
                        {
                            "source": twitter_user_id,
                            "title": title,
                            "link": link,
                            "pub_date": pub_date,
                            "external_id": tweet_external_id,
                            "tweet_type": tweet_type,
                        }
                    )
            else:
                break
            last_id = tweet_external_id
        except Exception as _:
            continue
    cache.set("last_id", last_id)
    new_articles = [
        Article(
            title=new_tweet["title"],
            link=new_tweet["link"],
            pub_date=new_tweet["pub_date"],
            source=sources.get(external_id=new_tweet["source"]),
            external_id=new_tweet["external_id"],
            tweet_type=new_tweet["tweet_type"],
        )
        for new_tweet in tweet_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Substack")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=substack_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in substack_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)
        sleep(6)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="SeekingAlpha")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=seekingalpha_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in seekingalpha_sources:
        feed_url = f"{source.url}.xml"
        create_articles_from_feed(source, feed_url, articles)
        sleep(15)


@shared_task
def scrape_other_websites():
    other_sources = (
        Source.objects.filter(website=get_object_or_404(Website, name="Other"))
        .exclude(external_id__isnull=False)
        .only("source_id", "url", "website")
    )
    articles = Article.objects.filter(source__in=other_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in other_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)


@shared_task
def scrape_forbes():
    forbes_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Forbes")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=forbes_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in forbes_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)
        sleep(5)


@shared_task
def scrape_spotify():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=spotify_sources).only(
        "title", "link", "source"
    )
    spotify_creation_list = []
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        try:
            episodes = spotify.get_episodes(source.external_id)
            episode_items = episodes["items"]
            for episode_item in episode_items:
                title = unescape(episode_item["name"])
                link = episode_item["external_urls"]["spotify"]
                # SpotifyAPI release_date only has date precision, so it always shows midnight => therefore better to use current time of scrapping
                spotify_creation_list, article_exists = article_creation_check(
                    spotify_creation_list, articles, title, source, link
                )
                if article_exists:
                    break
        except Exception as _:
            continue
    bulk_create_articles_and_notifications(spotify_creation_list)


@shared_task
def scrape_youtube():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=youtube_sources).only(
        "title", "pub_date", "link", "source"
    )
    youtube_creation_list = []
    for source in youtube_sources:
        channel_data = request_get(
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
            timeout=10,
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
        request = request_get(url, timeout=10)
        data = request.json()
        try:
            items = data["items"]
            for item in items:
                title = unescape(item["snippet"]["title"])
                link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                pub_date = item["snippet"]["publishedAt"]
                youtube_creation_list, article_exists = article_creation_check(
                    youtube_creation_list,
                    articles,
                    title,
                    source,
                    link,
                    pub_date=pub_date,
                )
                if article_exists:
                    break
        except Exception as _:
            continue
    bulk_create_articles_and_notifications(youtube_creation_list)


@shared_task
def twitter_scrape_followings():
    api = twitter_create_api_settings()
    followings = api.get_friends(count=100)
    for follow in followings:
        name = follow.name
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        if (
            Source.objects.filter(name=follow.name).exists()
            or Source.objects.filter(slug=slugify(name)).exists()
        ):
            name = follow.name + " - Twitter"
        url = f"https://twitter.com/{follow.screen_name}"
        slug = slugify(name)
        external_id = follow.id
        source = Source.objects.create(
            url=url,
            slug=slug,
            name=name,
            favicon_path=f"home/favicons/{slug}.png",
            paywall="No",
            website=get_object_or_404(Website, name="Twitter"),
            external_id=external_id,
        )
        source_profile_img_create(
            source, follow.profile_image_url_https.replace("_normal", "")
        )


@shared_task
def youtube_get_profile_images():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    for source in youtube_sources:
        try:
            url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
            request = request_get(url, timeout=10)
            data = request.json()
            source_profile_img_create(
                source, data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
            )
        except Exception as _:
            continue


@shared_task
def spotify_get_profile_images():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    )
    for source in spotify_sources:
        try:
            spotify = SpotifyAPI(client_id, client_secret)
            podcaster = spotify.get_podcaster(source.external_id)
            if "images" in podcaster.keys():
                source_profile_img_create(source, podcaster["images"][0]["url"])
            else:
                continue
        except Exception as _:
            continue


@shared_task
def old_notifications_delete():
    NotificationMessage.objects.filter(
        date__lte=timezone.now() - timedelta(hours=24)
    ).delete()


@shared_task
def youtube_delete_innacurate_articles():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    youtube_videos = []
    for source in youtube_sources:
        saved_articles_from_source = Article.objects.filter(source=source)
        channel_data = request_get(
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
            timeout=10,
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
        request = request_get(url, timeout=10)
        item_list = []
        next_item = True
        iterations = 0
        while next_item and iterations < 20:
            data = request.json()
            items = data["items"]
            item_list.append(items)
            if "nextPageToken" in data.keys():
                next_page_token = data["nextPageToken"]
                iterations += 1
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000&pageToken={next_page_token}"
                request = request_get(url, timeout=10)
            else:
                next_item = False
                break
        for items in item_list:
            try:
                for item in items:
                    title = unescape(item["snippet"]["title"])
                    link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    pub_date = item["snippet"]["publishedAt"]
                    youtube_videos.append(
                        {"title": title, "link": link, "pub_date": pub_date}
                    )
            except Exception as _:
                continue
        for article in saved_articles_from_source:
            if not any(d["title"] == article.title for d in youtube_videos) or not any(
                d["link"] == article.link
                for d in youtube_videos
                or not any(d["pub_date"] == article.pub_date for d in youtube_videos)
            ):
                article.delete()


@shared_task
def delete_tweet_types_empty():
    tweet_types = TweetType.objects.all()
    for tweet_type in tweet_types:
        if not tweet_type.tweet.all():
            tweet_type.delete()


@shared_task
def calc_sim_sources():
    Source.objects.calc_similiar_sources()


@shared_task
def create_spotify_sources():
    from apps.source.models import Sector, SourceRating

    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = [
        "https://open.spotify.com/show/16iCltJIbl8tB8sBi6SEP3",
        "https://open.spotify.com/show/5br8q17fDMJx6mmpuTw9SX",
        "https://open.spotify.com/show/3C0iP88KSoGZk5KNWmuyF1",
        "https://open.spotify.com/show/0mAhl79iQO2e12j5qdD38d",
        "https://open.spotify.com/show/7u9GPSNRk2B7vQcjyTrKiV",
        "https://open.spotify.com/show/7JhOkXo6DKXhmKZh4F7MP4",
        "https://open.spotify.com/show/2r75HRXpsJraJ3Akyo8kSg",
        "https://open.spotify.com/show/6E709HRH7XaiZrMfgtNCun",
        "https://open.spotify.com/show/6AVgt0Cx1Rnzrg2CBbEygM",
        "https://open.spotify.com/show/4zk8cAxOQFKXJWTxpdMr4C",
        "https://open.spotify.com/show/6Y1STt6SGDnPc8AdDzGMzn",
        "https://open.spotify.com/show/3Qbcrw84MDaJ3CZUNuqOxu",
        "https://open.spotify.com/show/7sLINDEeMqJyxs3h1Cp4Ub",
        "https://open.spotify.com/show/3q6PrjHVfRzpD2lN1g2XRU",
        "https://open.spotify.com/show/6Azh5lcMWsfvvMWRMVS9od",
        "https://open.spotify.com/show/7cRZcoh8fO0uJ9lwruKf4b",
        "https://open.spotify.com/show/4nrTAYb6qym9HZ1MO84ipz",
        "https://open.spotify.com/show/0sebfAmGcpda8OsQidlu3L",
        "https://open.spotify.com/show/3aqGbrhA31njZpzlFt1HyT",
        "https://open.spotify.com/show/00X0l59Bw9RMRMyKdsLk0H",
        "https://open.spotify.com/show/7the6Gr79b0W5SMczrAXOC",
        "https://open.spotify.com/show/5OXBdcyxYWOEcN8Y2aO6v9",
        "https://open.spotify.com/show/29duM2DReMHe1VjCTFP5S2",
        "https://open.spotify.com/show/0na7AKJGLDTJYcCDLAvqNQ",
        "https://open.spotify.com/show/1hBfrTaP5TwpsIvx51fTN9",
        "https://open.spotify.com/show/4EMek07KPxJYKdGOYiiHDv",
        "https://open.spotify.com/show/3GiTlGlvvDjmFctw4naowq",
        "https://open.spotify.com/show/4nzvXIY5HPuJpXPGeEUvkl",
        "https://open.spotify.com/show/3LGyb7VLIhcCP27ajT0JKQ",
        "https://open.spotify.com/show/2aqzxxFMfCT7pd52rXXrcZ",
        "https://open.spotify.com/show/1BdXQH894DNJnI1cTj5X86",
        "https://open.spotify.com/show/7mXQYIIWfhh2GWjDGxSx3H",
        "https://open.spotify.com/show/7yMLsm5s8tLtrCQr7bG8wD",
        "https://open.spotify.com/show/0TYNFdGwFOoBOluuAhSRc0",
        "https://open.spotify.com/show/7LYeomavBzwgQhJos7qrms",
        "https://open.spotify.com/show/4a3idqDVFpfOPdNH9fO8nG",
        "https://open.spotify.com/show/7gzvAJxpeAWLdUjdxunLIu",
        "https://open.spotify.com/show/3xdVf8ToW0R4nRfcNgwfyC",
        "https://open.spotify.com/show/2EXhvCQW0IEIDdCWik66tA",
        "https://open.spotify.com/show/57wZcoxW8oNs5Mq7WZfTs7",
        "https://open.spotify.com/show/2Uu2IFxc4DdjbTGHsCWLT8",
        "https://open.spotify.com/show/2LU5CNGlh7vGy1OYW83qco",
        "https://open.spotify.com/show/1dPPc2EX0MbSwuAaPeXqf3",
        "https://open.spotify.com/show/7vsf2QkL0P9Ac7dp3HyUg3",
        "https://open.spotify.com/show/507UG1K6xglIHxuRYjlI1n",
        "https://open.spotify.com/show/2qrjQTO7wFlkAs6juz1w1W",
        "https://open.spotify.com/show/4vk2MfVMEAuOnTWUOz6lnE",
        "https://open.spotify.com/show/1do6Oa0fxKFyw1Yt1IlBIk",
        "https://open.spotify.com/show/4fjb8YTzHDuPBgDXc3ElkR",
        "https://open.spotify.com/show/2OkpUUTl7dafPaS0DP0p5Q",
        "https://open.spotify.com/show/36gVeeoYns1RBASPLhAYeJ",
        "https://open.spotify.com/show/4QSHBYlMjTwwy1qK2mlM1F",
        "https://open.spotify.com/show/40JCARVTHpPOq4CmZuDaUN",
        "https://open.spotify.com/show/1lqdT5BMGiupKpC3j2iUEq",
        "https://open.spotify.com/show/7fud1Dmg6ZHMPl4aPgkon0",
        "https://open.spotify.com/show/23H0tOX63xMChV2SErQKnZ",
        "https://open.spotify.com/show/6o7el5KJdU4HnFI7zg2szp",
        "https://open.spotify.com/show/7tV2EIrKXXUPxO0jpUaLlX",
        "https://open.spotify.com/show/2rFbJfhplU2vifyhW00vHx",
        "https://open.spotify.com/show/7cPWOxfkyb1i8uffx13GDz",
        "https://open.spotify.com/show/6PNr3ml8nEQotWWavE9kQz",
        "https://open.spotify.com/show/5gHl65x4AikFNqeEeLowGw",
        "https://open.spotify.com/show/6zwovuEpg7Q7mDHZMw6UJC",
        "https://open.spotify.com/show/1sQB9P6FjNTn90rUHZciaT",
        "https://open.spotify.com/show/7fud1Dmg6ZHMPl4aPgkon0",
        "https://open.spotify.com/show/4wCAfhgUdspxeMqyi6KZkb",
        "https://open.spotify.com/show/62eiFvmcWsSPwZQhq2VvMD",
        "https://open.spotify.com/show/7wv1GJCQHcggXDdMHbhRlY",
        "https://open.spotify.com/show/0353WGU7UGrRBdqdHNm3K2",
        "https://open.spotify.com/show/1taxW9jHXvLCu6YCUxliIz",
        "https://open.spotify.com/show/7eAVfvaAVz7uiXSSQ9HPcQ",
        "https://open.spotify.com/show/1kYiUtgDcaUoMQjUko7toT",
        "https://open.spotify.com/show/4TWOlf80GM1Pml8fGUO8KK",
        "https://open.spotify.com/show/3xoeD59yjQ6R26wONtdQKB",
        "https://open.spotify.com/show/514P0q3t3AqW38aSCfTUoB",
        "https://open.spotify.com/show/23pjgFtojffb9ATqmOWoSG",
        "https://open.spotify.com/show/5NhjpDeHzVlXPVqT9ezKwA",
        "https://open.spotify.com/show/5qk8RnfIkb3peJJp4dsmvB",
        "https://open.spotify.com/show/3bh608DbMRZXHaBSjvhvHZ",
        "https://open.spotify.com/show/4vNumoS1tv284WNs6N8irH",
        "https://open.spotify.com/show/3qsBrXPv7IxyVdHvalT0zK",
        "https://open.spotify.com/show/5kmaGwX0xXwLl4ozXvW6jP",
        "https://open.spotify.com/show/2Y8gp7izc5VcNS7OJKD8QN",
        "https://open.spotify.com/show/7xF1lww4OCT34x7lK9iW52",
        "https://open.spotify.com/show/2jjxMaf00TlgajwqOd9wH5",
        "https://open.spotify.com/show/75qCFpgMCZeL1h1bLOaDUF",
        "https://open.spotify.com/show/5LWZLmUqnK2A9QKHKrkDWI",
        "https://open.spotify.com/show/3rdqvzvAvXv0LxnR8c93AK",
        "https://open.spotify.com/show/2NG24rv3Mv09EMsIc6rVfs",
        "https://open.spotify.com/show/30Uj92DHhMF2hP0uXyFt3l",
        "https://open.spotify.com/show/6RhitW2pBXlhKnXPVFF5Ok",
        "https://open.spotify.com/show/5mWMlenq9TcEZlgXey2qKY",
        "https://open.spotify.com/show/5IPy0HvQpAgu0kMjCqqUXS",
        "https://open.spotify.com/show/6w7pyZbdmMfKVqIn17HQPQ",
    ]
    failed_sources = []
    for source_url in spotify_sources:
        try:
            external_id = source_url.split("https://open.spotify.com/show/")[1]
            spotify = SpotifyAPI(client_id, client_secret)
            podcaster = spotify.get_podcaster(external_id)
            name = podcaster["name"]
            source = Source.objects.create(
                url=source_url,
                slug=slugify(name),
                name=name,
                favicon_path=f"home/favicons/{slugify(name)}.webp",
                paywall="No",
                website=get_object_or_404(Website, name="Spotify"),
                content_type="Analysis",
                sector=get_object_or_404(Sector, name="Generalists"),
            )
            if "images" in podcaster.keys():
                source_profile_img_create(source, podcaster["images"][0]["url"])
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=source,
                rating=7,
            )
        except Exception as error:
            failed_sources.append(source_url)
            print(f"Scrapping {source_url} failed due to {error}")
            continue
        sleep(3)
    print("Scrapping failed for these sources")
    for source in failed_sources:
        print(source)


# =================================================================================
# Tasks that need to be used from time to time
# =================================================================================


# @shared_task
# def stocks_create_all_companies_json():
#     api_key = environ.get("FMP_API_KEY")
#     url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
#     response = request_get(url, stream=True, timeout=10)
#     if response.status_code == 200:
#         with open("data_next.json", "w") as f:
#             for chunk in response.iter_content(chunk_size=1024):
#                 try:
#                     chunk_str = chunk.decode("utf-8", errors="ignore")
#                     f.write(chunk_str)
#                 except UnicodeDecodeError as err:
#                     print("UnicodeDecodeError:", err)


# @shared_task
# def stocks_create_models_from_json():
#     with open("all_companies_01042023.json", "r") as f:
#         company_data = json.load(f)
#     for item in company_data:
#         symbol = item["symbol"]
#         if (
#             item["type"] == "stock"
#             and all(char not in symbol for char in ("."))
#             and len(symbol) < 7
#         ):
#             if "-" in symbol:
#                 symbol = symbol.replace("-", ".")
#             full_name = item["name"]
#             short_name = full_name
#             for word in full_fillerwords:
#                 short_name = short_name.replace(word, "")
#             for word in short_fillerwords:
#                 short_name = short_name.replace(word, "")
#             stock_instance = Stock.objects.filter(ticker=symbol).first()
#             try:
#                 if stock_instance:
#                     stock_instance.full_company_name = full_name[:100]
#                     stock_instance.short_company_name = short_name[:100]
#                     stock_instance.save()
#                 elif Stock.objects.filter(full_company_name=full_name[:100]).exists():
#                     continue
#                 else:
#                     Stock.objects.create(
#                         ticker=symbol,
#                         full_company_name=full_name[:100],
#                         short_company_name=short_name[:100],
#                     )
#             except Exception as e:
#                 continue


# @shared_task
# def find_english_words():
#     # Load the words from the text file
#     with open("words.txt", "r") as f:
#         words = set(line.strip() for line in f)

#     # Create an empty list to store the matching words
#     english_words = []

#     # Loop through all instances of the Stock model
#     for stock in Stock.objects.all():
#         # Check if the ticker is in the words set
#         if stock.ticker.lower() in words:
#             english_words.append(stock.ticker.lower())
#         # Check if the short_company_name is in the words set
#         if stock.short_company_name.lower() in words:
#             english_words.append(stock.short_company_name.lower())

#     # Write the English words to a new Python file
#     with open("english_words.py", "w") as f:
#         f.write("english_words = {}\n".format(english_words))


# @shared_task
# def delete_article_duplicates():
#     sources = Source.objects.exclude(website__name="Twitter")
#     for source in sources:
#         ids_of_duplicate_articles = []
#         try:
#             articles_from_source = Article.objects.filter(source=source).order_by(
#                 "pub_date"
#             )
#             for article in articles_from_source:
#                 title_duplicates = articles_from_source.filter(title=article.title)
#                 duplicates = title_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         title_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             title_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#                 link_duplicates = articles_from_source.filter(link=article.link)
#                 duplicates = link_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         link_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             link_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#         except Exception as error:
#             print(error)
#         Article.objects.filter(article_id__in=ids_of_duplicate_articles).delete()


# @shared_task
# def forbes_scrape_accounts():
#     new_forbes_sources = []
#     failed_scrapping = []
#     for source_url in new_forbes_sources:
#         try:
#             print(source_url)
#             name, img_url = get_forbes_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#             ):
#                 name = name + " - Forbes"
#             source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.png",
#                 paywall="Semi",
#                 website=get_object_or_404(Website, name="Forbes"),
#                 content_type="News",
#             )
#             source_profile_img_create(source, img_url)
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=source,
#                 rating=7,
#             )
#             sleep(5)
#         except Exception as error:
#             failed_scrapping.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def seeking_alpha_scrape_accounts():
#     new_sources = [
#         # {
#         #     "url": "https://seekingalpha.com/author/best-anchor-stocks",
#         #     "name": "Best Anchor Stocks",
#         #     "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/205/028/extra_large_pic.png",
#         #     "rating": 8,
#         #     "sector": "Tech",
#         #     "tags": [],
#         # },
#     ]

#     failed_scrapping = []
#     for source in new_sources:
#         try:
#             print(source)
#             name_of_new_source = source["name"]
#             created_source = Source.objects.create(
#                 url=source["url"],
#                 slug=slugify(name_of_new_source),
#                 name=name_of_new_source,
#                 favicon_path=f"home/favicons/{slugify(name_of_new_source)}.png",
#                 paywall="Yes",
#                 website=get_object_or_404(Website, name="SeekingAlpha"),
#                 content_type="Analysis",
#                 sector=get_object_or_404(Sector, name=source["sector"]),
#             )
#             if len(source["tags"]):
#                 for tag in source["tags"]:
#                     created_source.tags.add(get_object_or_404(SourceTag, name=tag))
#             source_profile_img_create(created_source, source["profile_pic"])
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=created_source,
#                 rating=source["rating"],
#             )
#             sleep(5)
#         except Exception as error:
#             failed_scrapping.append(name_of_new_source)
#             print(f"Scrapping {name_of_new_source} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def substack_scrape_accounts():
#     new_substack_sources = []
#     for source_url in new_substack_sources:
#         try:
#             print(source_url)
#             name, img_url = get_substack_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#             ):
#                 name = name + " - Substack"
#             source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.png",
#                 paywall="Yes",
#                 website=get_object_or_404(Website, name="Substack"),
#             )
#             source_profile_img_create(source, img_url)
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=source,
#                 rating=7,
#             )
#             sleep(5)
#         except Exception as error:
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
