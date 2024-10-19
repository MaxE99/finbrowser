from typing import Any
import os
from html import unescape
import traceback

from django.core.management.base import BaseCommand

from apps.tasks.utils import (
    bulk_create_articles_and_notifications,
    perform_article_status_check,
    get_spotify_sources_and_articles,
)
from apps.tasks.spotify_api import SpotifyAPI


class Command(BaseCommand):
    """
    Django management command to scrape Spotify for episodes.

    This command retrieves episodes from Spotify sources and
    creates corresponding articles and notifications in the database.
    """

    help = "Scrapes Spotify for podcast episodes and creates articles."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape Spotify episodes and create articles.

        This method fetches Spotify sources, retrieves episodes for each
        source, checks if articles already exist for those episodes, and
        bulk creates articles and notifications.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """

        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        spotify_data = get_spotify_sources_and_articles()
        spotify_creation_list = []

        for source in spotify_data["sources"]:
            spotify = SpotifyAPI(client_id, client_secret)

            try:
                episodes = spotify.get_episodes(source.external_id)
                episode_items = episodes["items"]

                for episode_item in episode_items:
                    title = unescape(episode_item["name"])
                    link = episode_item["external_urls"]["spotify"]
                    # SpotifyAPI release_date only has date precision, so it always shows midnight => therefore better to use current time of scrapping
                    lists = perform_article_status_check(
                        spotify_creation_list,
                        spotify_data["articles"],
                        title,
                        source,
                        link,
                    )
                    spotify_creation_list = lists["creation_list"]

                    if lists["article_exists"]:
                        break

            except Exception as _:
                print(f"Fetching items from {source} failed due to: ")
                traceback.print_exc()
                continue

        bulk_create_articles_and_notifications(spotify_creation_list)
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully scraped Spotify episodes and created articles!"
            )
        )
