from typing import Any

from django.core.management.base import BaseCommand

from apps.tasks.utils import scrape_sources


class Command(BaseCommand):
    """
    Django management command to scrape articles from various websites.

    This command initiates the scraping process for articles from
    websites classified under 'Other'.
    """

    help = "Scrapes articles from websites categorized as 'Other'."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to scrape articles from other websites.

        This method calls the `scrape_sources` function with the specific
        parameters for sources classified as 'Other'.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        scrape_sources("Other", "feed"),
        self.stdout.write(
            self.style.SUCCESS("Successfully scraped articles from 'Other' websites!")
        )
