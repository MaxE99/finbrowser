from django.urls import path, re_path

from apps.stock.views import StockDetailView, PortfolioView, PortfolioDetailView


app_name = "stock"


# Define a custom route converter to accept a slug with a point
class SlugWithPointConverter:
    regex = r"[\w\-\.]+"


urlpatterns = [
    re_path(
        r"^stock/(?P<slug_with_point>[\w\-\.]+)$",
        StockDetailView.as_view(),
        name="stock-details",
    ),
    path("portfolio/", PortfolioView.as_view(), name="portfolio"),
    path(
        "portfolio/<int:portfolio_id>",
        PortfolioDetailView.as_view(),
        name="portfolio-details",
    ),
]
