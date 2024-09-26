from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import scrape_sources


class Command(BaseCommand):
    help = "Scrapes Substack"

    def handle(self, *args, **kwargs):
        scrape_sources("Substack", "feed", 10),
        self.stdout.write("Finished scraping substack!")
