from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import scrape_sources


class Command(BaseCommand):
    help = "Scrapes Forbes"

    def handle(self, *args, **kwargs):
        scrape_sources("Forbes", "feed", 10),
        self.stdout.write("Finished scraping forbes!")
