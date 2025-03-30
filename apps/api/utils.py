from typing import Any, Dict, List

from apps.api.serializers import (
    SourceSerializer,
    ArticleSerializer,
    StockSerializer,
)
from apps.stock.models import Portfolio, PortfolioStock, Stock
from apps.source.models import Source
from apps.article.models import Article


def balance_search_results(
    filtered_stocks: List[Stock],
    filtered_sources: List[Source],
    filtered_articles: List[Article],
) -> Dict[str, Any]:
    """
    Balances the number of displayed stocks, sources, and articles based on their availability.

    Args:
        filtered_stocks (List[Stock]): The filtered stocks to balance.
        filtered_sources (List[Source]): The filtered sources to balance.
        filtered_articles (List[Article]): The filtered articles to balance.

    Returns:
        Dict[str, Any]:
            Serializers for stocks, sources, and articles with adjusted display counts.
    """

    len_filtered_stocks = filtered_stocks.count()
    len_filtered_sources = filtered_sources.count()
    len_filtered_articles = filtered_articles.count()

    display_spots_stocks = min(3, len_filtered_stocks)
    display_spots_sources = min(3, len_filtered_sources)
    display_spots_articles = min(3, len_filtered_articles)

    total_display_spots = (
        display_spots_stocks + display_spots_sources + display_spots_articles
    )

    # Incrementally increase display spots until reaching a minimum of 9 total
    while total_display_spots < 9:
        if len_filtered_stocks > display_spots_stocks:
            display_spots_stocks += 1
        if len_filtered_sources > display_spots_sources:
            display_spots_sources += 1
        if len_filtered_articles > display_spots_articles:
            display_spots_articles += 1

        total_display_spots = (
            display_spots_stocks + display_spots_sources + display_spots_articles
        )

        # Break if there are no more items left to increment
        if (
            display_spots_stocks == len_filtered_stocks
            and display_spots_sources == len_filtered_sources
            and display_spots_articles == len_filtered_articles
        ):
            break

    stock_serializer = StockSerializer(
        filtered_stocks[:display_spots_stocks], many=True
    )
    sources_serializer = SourceSerializer(
        filtered_sources[:display_spots_sources], many=True
    )
    articles_serializer = ArticleSerializer(
        filtered_articles[:display_spots_articles], many=True
    )

    return {
        "stock_serializer": stock_serializer,
        "articles_serializer": articles_serializer,
        "sources_serializer": sources_serializer,
    }


def get_amount_portfolio_search_terms(portfolio: Portfolio) -> int:
    """
    Count the total number of search terms in a given portfolio.

    Args:
        portfolio (Portfolio): The portfolio to count search terms from.

    Returns:
        int: The total count of search terms (including keywords and stocks).
    """
    search_terms = 0
    stocks = PortfolioStock.objects.filter(portfolio=portfolio)

    for stock in stocks:
        search_terms += stock.keywords.count() + 1

    return search_terms
