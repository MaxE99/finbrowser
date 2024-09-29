from typing import Any, List, Tuple, Union

from django.db.models import Q

from data.english_words import english_words
from apps.stock.models import PortfolioStock
from apps.article.models import Article


def stocks_get_experts(filtered_content: List[Any]) -> List[List[Any]]:
    """
    Analyzes the filtered content and categorizes sources based on their content type.

    Args:
        filtered_content (List[Any]): The list of filtered articles or content.

    Returns:
        List[List[Any]]: A list containing three lists of sources categorized by:
            - Analysis sources
            - Commentary sources
            - News sources
    """
    sources_articles_written = {}
    for content in filtered_content:
        if content.source in sources_articles_written.keys():
            sources_articles_written[content.source] += 1
        else:
            sources_articles_written[content.source] = 1
    sorted_sources = dict(
        sorted(sources_articles_written.items(), key=lambda item: item[1], reverse=True)
    )

    analysis_sources = []
    commentary_sources = []
    news_sources = []

    for source in sorted_sources:
        if source.content_type == "Analysis" and len(analysis_sources) < 16:
            analysis_sources.append(source)
        elif source.content_type == "Commentary" and len(commentary_sources) < 16:
            commentary_sources.append(source)
        elif source.content_type == "News" and len(news_sources) < 16:
            news_sources.append(source)

    return [analysis_sources, commentary_sources, news_sources]


def create_portfolio_search_object(stocks: List[PortfolioStock]) -> Q:
    """
    Create a Q object for filtering articles based on stock tickers,
    short company names, and associated keywords.

    Args:
        stocks (List[PortfolioStock]): A list of portfolio stocks to create the search query from.

    Returns:
        Q: A Q object that can be used for filtering articles.
    """
    q_objects = Q()
    for stock in stocks:
        ticker = stock.stock.ticker
        short_name = stock.stock.short_company_name

        if len(ticker) > 1 and ticker.lower() not in english_words:
            q_objects.add(Q(search_vector=ticker), Q.OR)

        if short_name.lower() not in english_words:
            q_objects.add(Q(search_vector=short_name), Q.OR)

        for keyword in stock.keywords.all():
            if keyword.keyword not in english_words:
                q_objects.add(Q(search_vector=keyword.keyword), Q.OR)

    return q_objects


def create_content_lists(
    content_list: List[Union[Article]],
) -> Tuple[List[Article], List[Article], List[Article]]:
    """
    Categorize articles into analysis, commentary, and news based on their content type.

    Args:
        content_list (List[Union[Article]]): A list of articles to categorize.

    Returns:
        Tuple[List[Article], List[Article], List[Article]]: A tuple containing three lists of articles:
        analysis content, commentary content, and news content.
    """
    analysis_content = []
    commentary_content = []
    news_content = []

    for article in content_list:

        if article.source.content_type == "Analysis":
            analysis_content.append(article)
        elif article.source.content_type == "Commentary":
            commentary_content.append(article)
        else:
            news_content.append(article)

    return analysis_content, commentary_content, news_content
