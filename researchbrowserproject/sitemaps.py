from typing import List

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.source.models import Source
from apps.sector.models import Sector
from apps.stock.models import Stock


class RegistrationSitemaps(Sitemap):
    """
    Sitemap for user account-related URLs.

    This sitemap includes paths for login and signup pages, with a
    change frequency of monthly and a priority of 0.6.
    """

    changefreq = "monthly"
    priority = 0.6
    protocol = "https"

    def items(self) -> List[str]:
        """
        Returns a list of URL names related to user account actions.

        Returns:
            List[str]: A list containing URL names for login and signup.
        """
        return ["account_login", "account_signup"]

    def location(self, item: str) -> str:
        """
        Returns the URL for a given item.

        Args:
            item (str): The name of the URL to reverse.

        Returns:
            str: The full URL for the given item.
        """
        return reverse(item)


class SourceSitemap(Sitemap):
    """
    Sitemap for source profiles.

    This sitemap includes all source profiles with an hourly change
    frequency and a high priority of 1.0.
    """

    changefreq = "hourly"
    priority = 1.0
    protocol = "https"

    def items(self) -> List[Source]:
        """
        Returns all Source objects to be included in the sitemap.

        Returns:
            List[Source]: A list of Source instances.
        """
        return Source.objects.all()

    def location(self, obj: Source) -> str:
        """
        Returns the URL for a given source profile.

        Args:
            obj (Source): The Source object for which to get the URL.

        Returns:
            str: The full URL for the source profile.
        """
        return reverse("source:source_profile", args=[obj.slug])


class StockSitemap(Sitemap):
    """
    Sitemap for stock details.

    This sitemap includes all stocks with an hourly change frequency
    and a priority of 0.9.
    """

    changefreq = "hourly"
    priority = 0.9
    protocol = "https"

    def items(self) -> List[Stock]:
        """
        Returns all Stock objects to be included in the sitemap.

        Returns:
            List[Stock]: A list of Stock instances.
        """
        return Stock.objects.all()

    def location(self, obj: Stock) -> str:
        """
        Returns the URL for a given stock's details.

        Args:
            obj (Stock): The Stock object for which to get the URL.

        Returns:
            str: The full URL for the stock details.
        """
        return reverse("stock:stock-details", args=[obj.ticker])


class SectorSitemap(Sitemap):
    """
    Sitemap for sector details.

    This sitemap includes all sectors with an hourly change frequency
    and a priority of 0.8.
    """

    changefreq = "hourly"
    priority = 0.8
    protocol = "https"

    def items(self) -> List[Sector]:
        """
        Returns all Sector objects to be included in the sitemap.

        Returns:
            List[Sector]: A list of Sector instances.
        """
        return Sector.objects.all()

    def location(self, obj: Sector) -> str:
        """
        Returns the URL for a given sector's details.

        Args:
            obj (Sector): The Sector object for which to get the URL.

        Returns:
            str: The full URL for the sector details.
        """
        return reverse("sector:sector-details", args=[obj.slug])


class ContentSitemaps(Sitemap):
    """
    Sitemap for content-related URLs.

    This sitemap includes various content-related pages with an hourly
    change frequency and a priority of 0.9.
    """

    changefreq = "hourly"
    priority = 0.9
    protocol = "https"

    def items(self) -> List[str]:
        """
        Returns a list of URL names for various content-related pages.

        Returns:
            List[str]: A list containing URL names for content pages.
        """
        return ["home:feed", "home:guide", "source:source_ranking"]

    def location(self, item: str) -> str:
        """
        Returns the URL for a given content item.

        Args:
            item (str): The name of the URL to reverse.

        Returns:
            str: The full URL for the given content item.
        """
        return reverse(item)
