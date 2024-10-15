from typing import Any

from django.core.management.base import BaseCommand

from apps.tasks.utils import scrape_sources


class Command(BaseCommand):
    """
    Django management command to scrape articles from Seeking Alpha.

    This command initiates the scraping process for articles from
    the Seeking Alpha website.
    """

    help = "Scrapes articles from Seeking Alpha."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape articles from Seeking Alpha.

        This method calls the `scrape_sources` function with the specific
        parameters for the Seeking Alpha source.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        scrape_sources("SeekingAlpha", ".xml", timeout=15),
        self.stdout.write(
            self.style.SUCCESS("Successfully scraped articles from Seeking Alpha!")
        )
