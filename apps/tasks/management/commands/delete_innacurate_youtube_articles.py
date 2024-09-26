# Python imports
from html import unescape
from os import environ
import requests


# Django imports
from django.shortcuts import get_object_or_404
from django.core.management.base import BaseCommand


# Local imports
from apps.article.models import Article
from apps.accounts.models import Website
from apps.source.models import Source


class Command(BaseCommand):
    help = "Deletes innacurate YouTube articles"

    def handle(self, *args, **kwargs):
        api_key = environ.get("YOUTUBE_API_KEY")
        youtube_sources = Source.objects.filter(
            website=get_object_or_404(Website, name="YouTube")
        )
        youtube_videos = []
        for source in youtube_sources:
            saved_articles_from_source = Article.objects.filter(source=source)
            channel_data = requests.get(
                f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
                timeout=10,
            ).json()
            upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
                "uploads"
            ]
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
            request = requests.get(url, timeout=10)
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
                    request = requests.get(url, timeout=10)
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
                if not any(
                    d["title"] == article.title for d in youtube_videos
                ) or not any(
                    d["link"] == article.link
                    for d in youtube_videos
                    or not any(
                        d["pub_date"] == article.pub_date for d in youtube_videos
                    )
                ):
                    article.delete()
        self.stdout.write("Finished deleting innacurate YouTube articles!")
