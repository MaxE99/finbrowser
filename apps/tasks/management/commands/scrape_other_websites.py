from django.core.management.base import BaseCommand

# Local imports
from apps.tasks.helpers import scrape_sources


class Command(BaseCommand):
    help = "Scrapes other websites"

    def handle(self, *args, **kwargs):
        scrape_sources("Other", "feed"),
        self.stdout.write("Finished scraping other websites!")
