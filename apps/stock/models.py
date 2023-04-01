# Django imports
from django.db import models
from django.urls import reverse
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Model imports
from apps.stock.managers import StockManager
from apps.source.models import Source
from django.contrib.auth import get_user_model

User = get_user_model()


class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    ticker = models.CharField(max_length=10, unique=True)
    full_company_name = models.CharField(max_length=100)
    short_company_name = models.CharField(max_length=100, db_index=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ("ticker",)
        indexes = (GinIndex(fields=["search_vector"]),)

    objects = StockManager()

    def get_absolute_url(self):
        return reverse("stock:stock-details", kwargs={"slug": self.ticker})

    def __str__(self):
        return f"{self.ticker} - {self.full_company_name} - {self.short_company_name}"


class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=30, validators=[MinLengthValidator(1), MaxLengthValidator(30)]
    )
    main = models.BooleanField(default=False)
    blacklisted_sources = models.ManyToManyField(
        Source, related_name="blacklisted_sources_portfolio", blank=True
    )

    def __str__(self):
        return f"{self.user}: {self.name}"

    def get_absolute_url(self):
        return reverse(
            "stock:portfolio-details", kwargs={"portfolio_id": self.portfolio_id}
        )


class PortfolioKeyword(models.Model):
    pkeyword_id = models.AutoField(primary_key=True)
    keyword = models.CharField(
        max_length=30, validators=[MinLengthValidator(3), MaxLengthValidator(30)]
    )

    def __str__(self) -> str:
        return f"{self.pkeyword_id}: {self.keyword}"


class PortfolioStock(models.Model):
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
        return f"{self.portfolio}: {self.stock}"
