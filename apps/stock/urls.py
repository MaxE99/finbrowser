# Django imports
from django.urls import path

# Local imports
from apps.stock.views import StockDetailView, PortfolioView, PortfolioDetailView


app_name = "stock"

urlpatterns = [
    path("stock/<slug:slug>", StockDetailView.as_view(), name="stock-details"),
    path("portfolio/", PortfolioView.as_view(), name="portfolio"),
    path(
        "portfolio/<int:portfolio_id>",
        PortfolioDetailView.as_view(),
        name="portfolio-details",
    ),
]
