from typing import Any

from django.core.management.base import BaseCommand

from apps.tasks.utils import scrape_sources


class Command(BaseCommand):
    """
    Django management command to scrape articles from Substack.

    This command initiates the scraping process for articles from
    the Substack platform.
    """

    help = "Scrapes articles from Substack."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape articles from Substack.

        This method calls the `scrape_sources` function with the specific
        parameters for the Substack source.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        scrape_sources("Substack", "feed", timeout=10),
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully completed scraping articles from Substack!"
            )
        )
