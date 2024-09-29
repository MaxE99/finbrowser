from django.db import models
from django.urls import reverse
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model

from apps.stock.managers import StockManager
from apps.source.models import Source

User = get_user_model()


class Stock(models.Model):
    """
    Represents a stock entity with its basic details.
    """

    stock_id = models.AutoField(primary_key=True)
    ticker = models.CharField(max_length=10, unique=True)
    full_company_name = models.CharField(max_length=100)
    short_company_name = models.CharField(max_length=100, db_index=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ("ticker",)
        indexes = (GinIndex(fields=["search_vector"]),)

    objects = StockManager()

    def get_absolute_url(self) -> str:
        """
        Returns the URL for the stock's detail view.

        Returns:
            str: The URL for the stock detail page.
        """
        return reverse("stock:stock-details", kwargs={"slug_with_point": self.ticker})

    def __str__(self) -> str:
        """
        Returns a string representation of the stock.

        Returns:
            str: A string in the format of "ticker - full_company_name - short_company_name".
        """
        return f"{self.ticker} - {self.full_company_name} - {self.short_company_name}"


class Portfolio(models.Model):
    """
    Represents a user's investment portfolio.
    """

    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=30, validators=[MinLengthValidator(1), MaxLengthValidator(30)]
    )
    main = models.BooleanField(default=False)
    blacklisted_sources = models.ManyToManyField(
        Source, related_name="blacklisted_sources_portfolio", blank=True
    )

    def get_absolute_url(self) -> str:
        """
        Returns the URL for the portfolio's detail view.

        Returns:
            str: The URL for the portfolio detail page.
        """
        return reverse(
            "stock:portfolio-details", kwargs={"portfolio_id": self.portfolio_id}
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the portfolio.

        Returns:
            str: A string in the format of "user: name".
        """
        return f"{self.user}: {self.name}"


class PortfolioKeyword(models.Model):
    """
    Represents a keyword associated with a portfolio.
    """

    pkeyword_id = models.AutoField(primary_key=True)
    keyword = models.CharField(
        max_length=30, validators=[MinLengthValidator(3), MaxLengthValidator(30)]
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the portfolio keyword.

        Returns:
            str: A string in the format of "pkeyword_id: keyword".
        """
        return f"{self.pkeyword_id}: {self.keyword}"


class PortfolioStock(models.Model):
    """
    Represents a stock within a portfolio.
    """

    pstock_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(
        PortfolioKeyword, related_name="portfolio_stocks", blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "stock"], name="unique_portfolio_stock"
            )
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the portfolio stock association.

        Returns:
            str: A string in the format of "portfolio: stock".
        """
        return f"{self.portfolio}: {self.stock}"
