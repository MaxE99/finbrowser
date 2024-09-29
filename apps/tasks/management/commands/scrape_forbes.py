from typing import Any

from django.core.management.base import BaseCommand

from apps.tasks.utils import scrape_sources


class Command(BaseCommand):
    """
    Django management command to scrape articles from Forbes.

    This command initiates the scraping process for Forbes articles
    using the defined scraping helper function.
    """

    help = "Scrapes the latest articles from Forbes."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape Forbes articles.

        This method calls the `scrape_sources` function with the specific
        parameters for Forbes.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        scrape_sources("Forbes", "feed", 10),
        self.stdout.write(self.style.SUCCESS("Successfully scraped Forbes articles!"))
