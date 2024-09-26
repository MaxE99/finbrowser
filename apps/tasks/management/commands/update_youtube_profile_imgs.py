# Python imports
from os import environ
import requests


# Django imports
from django.shortcuts import get_object_or_404
from django.core.management.base import BaseCommand


# Local imports
from apps.logic.services import source_profile_img_create
from apps.accounts.models import Website
from apps.source.models import Source


class Command(BaseCommand):
    help = "Updates profile images of YouTube sources"

    def handle(self, *args, **kwargs):
        api_key = environ.get("YOUTUBE_API_KEY")
        youtube_sources = Source.objects.filter(
            website=get_object_or_404(Website, name="YouTube")
        )
        for source in youtube_sources:
            try:
                url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
                request = requests.get(url, timeout=10)
                data = request.json()
                if "items" in data:
                    source_profile_img_create(
                        source,
                        data["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
                    )
                else:
                    print(f"{source} has no key items!")
            except Exception as error:
                print(f"Scrapping {source} has caused this error: {error}")
                continue
        self.stdout.write("Finished updating profile images of YouTube sources!")
