from typing import Any

from django.core.management.base import BaseCommand

from apps.tasks.utils import scrape_sources


class Command(BaseCommand):
    """
    Django management command to scrape articles from alternative feeds.

    This command initiates the scraping process for articles from
    sources classified under 'Alt Feed'.
    """

    help = "Scrapes articles from sources classified as 'Alt Feed'."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape articles from alternative feed sources.

        This method calls the `scrape_sources` function with the specific
        parameters for sources classified as 'Alt Feed'.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        scrape_sources("Alt Feed", "feed", alt_feed=True)
        self.stdout.write(
            self.style.SUCCESS("Successfully scraped articles from 'Alt Feed' sources!")
        )
