from html import unescape
import os

# from requests import get as request_get
import requests
from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import (
    bulk_create_articles_and_notifications,
    article_creation_check,
    get_youtube_sources_and_articles,
)


class Command(BaseCommand):
    help = "Scrapes YouTube"

    def handle(self, *args, **kwargs):
        api_key = os.environ.get("YOUTUBE_API_KEY")
        sources, articles = get_youtube_sources_and_articles()
        youtube_creation_list = []
        for source in sources:
            try:
                channel_data = requests.get(
                    f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
                    timeout=10,
                ).json()
                upload_id = channel_data["items"][0]["contentDetails"][
                    "relatedPlaylists"
                ]["uploads"]
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
                request = requests.get(url, timeout=10)
                data = request.json()
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
            except Exception as error:
                print(f"Scrapping {source} has caused this error: {error}")
                continue
        bulk_create_articles_and_notifications(youtube_creation_list)
        self.stdout.write("Finished scraping youtube!")
