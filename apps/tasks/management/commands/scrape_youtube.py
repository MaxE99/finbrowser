from typing import Any
from html import unescape
import os

import requests

from django.core.management.base import BaseCommand

from apps.tasks.utils import (
    bulk_create_articles_and_notifications,
    perform_article_status_check,
    get_youtube_sources_and_articles,
)


class Command(BaseCommand):
    """
    Django management command to scrape YouTube channels for videos.

    This command retrieves videos from YouTube sources and
    creates corresponding articles and notifications in the database.
    """

    help = "Scrapes YouTube channels for videos and updates the database."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape YouTube videos and create articles.

        This method fetches YouTube sources, retrieves videos for each
        source, checks if articles already exist for those videos, and
        bulk creates articles and notifications.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        api_key = os.environ.get("YOUTUBE_API_KEY")
        youtube_data = get_youtube_sources_and_articles()
        youtube_creation_list = []

        for source in youtube_data["sources"]:
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
                    lists = perform_article_status_check(
                        youtube_creation_list,
                        youtube_data["articles"],
                        title,
                        source,
                        link,
                        pub_date=pub_date,
                    )
                    youtube_creation_list = lists["creation_list"]

                    if lists["article_exists"]:
                        break

            except Exception as error:
                print(f"Scrapping {source} has caused this error: {error}")
                continue

        bulk_create_articles_and_notifications(youtube_creation_list)
        self.stdout.write(
            self.style.SUCCESS("Successfully completed scraping YouTube channels!")
        )
