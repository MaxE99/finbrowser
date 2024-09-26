from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import scrape_sources


class Command(BaseCommand):
    help = "Scrapes alternative feeds"

    def handle(self, *args, **kwargs):
        scrape_sources("Alt Feed", "feed", alt_feed=True)
        self.stdout.write("Finished scraping alternative feeds!")
