from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import scrape_sources


class Command(BaseCommand):
    help = "Scrapes SeekingAlpha"

    def handle(self, *args, **kwargs):
        scrape_sources("SeekingAlpha", ".xml", 15),
        self.stdout.write("Finished scraping seeking alpha!")
