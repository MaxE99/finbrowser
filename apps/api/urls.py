# Django imports
from django.urls import path, include
from rest_framework import routers

# Local imports
from apps.api.api import (
    FilteredSite,
    ListViewSet,
    NotificationViewSet,
    SourceViewSet,
    ProfileViewSet,
    SourceRatingViewSet,
    HighlightedArticleViewSet,
    SourceTagViewSet,
    PortfolioViewSet,
    StockViewSet,
    PortfolioStockViewSet,
    PortfolioKeywordViewSet,
    ArticleViewSet,
    remove_stock_from_portfolio,
)

app_name = "api"

router = routers.DefaultRouter()
router.register("lists", ListViewSet)
router.register("sources", SourceViewSet)
router.register("profiles", ProfileViewSet)
router.register("source_ratings", SourceRatingViewSet)
router.register("highlighted_articles", HighlightedArticleViewSet)
router.register("notifications", NotificationViewSet)
router.register("source_tags", SourceTagViewSet)
router.register("portfolios", PortfolioViewSet)
router.register("stocks", StockViewSet)
router.register("portfolio_stocks", PortfolioStockViewSet)
router.register("portfolio_keywords", PortfolioKeywordViewSet)
router.register("articles", ArticleViewSet)

urlpatterns = [
    path(
        "portfolio_stocks/remove_stock_from_portfolio/<int:portfolio_id>/<int:stock_id>",
        remove_stock_from_portfolio,
    ),
    path("search_site/<str:search_term>", FilteredSite.as_view()),
    path("", include(router.urls)),
]
