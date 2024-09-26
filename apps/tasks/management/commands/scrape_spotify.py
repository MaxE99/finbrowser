# Python imports
from html import unescape
from os import environ

import requests
from django.utils import timezone
from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import (
    bulk_create_articles_and_notifications,
    article_creation_check,
    get_spotify_sources_and_articles,
)
from apps.tasks.spotify_api import SpotifyAPI


class Command(BaseCommand):
    help = "Scrapes Spotify"

    def handle(self, *args, **kwargs):
        client_id = environ.get("SPOTIFY_CLIENT_ID")
        client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
        spotify_sources, articles = get_spotify_sources_and_articles()
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
        self.stdout.write("Finished scraping spotify!")
