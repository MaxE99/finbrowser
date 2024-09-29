from typing import Any
import os

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.tasks.utils import create_source_profile_img
from apps.accounts.models import Website
from apps.source.models import Source
from apps.tasks.spotify_api import SpotifyAPI


User = get_user_model()


class Command(BaseCommand):
    """
    Django management command to update profile images of Spotify sources.

    This command retrieves Spotify sources and updates their profile images
    based on the data fetched from the Spotify API.
    """

    help = "Fetches Spotify sources and updates their profile images."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to update profile images of Spotify sources.

        This method fetches Spotify sources from the database, retrieves
        the podcaster data from the Spotify API, and updates the source
        profile images accordingly.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

        spotify_sources = Source.objects.filter(
            website=get_object_or_404(Website, name="Spotify")
        )

        for source in spotify_sources:
            try:
                spotify = SpotifyAPI(client_id, client_secret)
                podcaster = spotify.get_podcaster(source.external_id)

                if "images" in podcaster.keys():
                    create_source_profile_img(source, podcaster["images"][0]["url"])

            except Exception as _:
                continue

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated profile images of Spotify sources!"
            )
        )
