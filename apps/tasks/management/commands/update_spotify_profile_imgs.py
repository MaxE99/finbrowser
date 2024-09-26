# Python imports
from os import environ
import requests


# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


# Local imports
from apps.logic.services import source_profile_img_create
from apps.accounts.models import Website
from apps.source.models import Source
from apps.tasks.spotify_api import SpotifyAPI


User = get_user_model()


class Command(BaseCommand):
    help = "Updates profile images of Spotify sources"

    def handle(self, *args, **kwargs):
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
        self.stdout.write("Finished updating profile images of Spotify sources!")
