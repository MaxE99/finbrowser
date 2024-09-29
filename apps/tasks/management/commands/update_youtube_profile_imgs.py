from typing import Any
import os

import requests

from django.shortcuts import get_object_or_404
from django.core.management.base import BaseCommand

from apps.tasks.utils import create_source_profile_img
from apps.accounts.models import Website
from apps.source.models import Source


class Command(BaseCommand):
    """
    Django management command to update profile images of YouTube sources.

    This command retrieves YouTube sources and updates their profile images
    based on the data fetched from the YouTube API.
    """

    help = "Fetches YouTube sources and updates their profile images."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to update profile images of YouTube sources.

        This method fetches YouTube sources from the database, retrieves
        the channel data from the YouTube API, and updates the source
        profile images accordingly.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        api_key = os.environ.get("YOUTUBE_API_KEY")
        youtube_sources = Source.objects.filter(
            website=get_object_or_404(Website, name="YouTube")
        )

        for source in youtube_sources:
            try:
                url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
                request = requests.get(url, timeout=10)
                data = request.json()

                if "items" in data:
                    create_source_profile_img(
                        source,
                        data["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
                    )
                else:
                    print(f"{source} has no key items!")

            except Exception as error:
                print(f"Scrapping {source} has caused this error: {error}")
                continue

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated profile images of YouTube sources!"
            )
        )
