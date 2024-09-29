from typing import Any, Dict, Optional

from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models

from apps.utils import create_paginator
from apps.stock.utils import (
    stocks_get_experts,
    create_portfolio_search_object,
    create_content_lists,
)
from apps.home.views import BaseMixin
from apps.stock.models import Stock, Portfolio, PortfolioStock
from apps.article.models import Article
from apps.home.models import Notification
from apps.stock.serializers import PortfolioStockSerializer, PortfolioSerializer


class StockDetailView(DetailView, BaseMixin):
    """
    View for displaying the details of a specific stock.

    Inherits from Django's DetailView and a custom BaseMixin. This view
    retrieves stock details and related articles, and provides context
    for rendering the stock details template.
    """

    model = Stock
    context_object_name = "stock"
    template_name = "stock/stock_details.html"

    def get_object(self, queryset: Optional[models.QuerySet] = None) -> Stock:
        """
        Retrieves the stock object based on the ticker provided in the URL.

        Args:
            queryset (Optional[QuerySet]): An optional queryset to filter the stock.

        Returns:
            Stock: The stock object retrieved from the database.

        Raises:
            Http404: If no stock with the provided ticker is found.
        """
        slug_with_point = self.kwargs["slug_with_point"]
        return get_object_or_404(Stock, ticker=slug_with_point)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves the context data for rendering the stock details template.

        Args:
            **kwargs (Any): Additional keyword arguments passed to the method.

        Returns:
            Dict[str, Any]: Context data to be used in the template, including:
                - Portfolios of the authenticated user
                - Notification ID for the stock
                - Articles related to the stock filtered by type (analysis, commentary, news)
        """
        context = super().get_context_data(**kwargs)
        stock = self.get_object()
        filtered_content = Article.objects.get_content_about_stock(stock)
        analysis_sources, commentary_sources, news_sources = stocks_get_experts(
            filtered_content
        )

        if self.request.user.is_authenticated:
            context["portfolios"] = PortfolioSerializer(
                Portfolio.objects.filter(user=self.request.user).order_by("name"),
                many=True,
            ).data
            context["notification_id"] = (
                Notification.objects.check_stock_notification_exists(
                    self.request.user, stock
                )
            )

        context["analysis_sources"] = analysis_sources
        context["commentary_sources"] = commentary_sources
        context["news_sources"] = news_sources
        context["analysis"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            25,
            "analysis",
        )
        context["commentary"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            25,
            "commentary",
        )
        context["news"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="News"),
            25,
            "news",
        )
        return context


class PortfolioView(TemplateView, BaseMixin):
    """
    View for displaying a user's stock portfolio.

    Inherits from Django's TemplateView and a custom BaseMixin. This view
    retrieves the selected portfolio and its associated stocks, filtering
    relevant articles based on the stocks in the portfolio.
    """

    template_name = "stock/portfolio.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves the context data for rendering the user's portfolio.

        Args:
            **kwargs (Any): Additional keyword arguments passed to the method.

        Returns:
            Dict[str, Any]: Context data to be used in the template, including:
                - Stocks in the selected portfolio
                - Selected portfolio
                - All user portfolios
                - Filtered articles categorized by type (analysis, commentary, news)
        """
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        selected_portfolio = get_object_or_404(
            Portfolio, user=self.request.user, main=True
        )
        stocks = (
            PortfolioStock.objects.filter(portfolio=selected_portfolio)
            .select_related("stock")
            .prefetch_related("keywords", "portfolio")
            .order_by("stock__ticker")
        )

        # check if the portfolio has any stocks to avoid timeout errors
        if stocks.exists():
            q_objects = create_portfolio_search_object(stocks)

            # potential edge case only stock in portfolio (e.g. Bill which will lead to no english words because of english word in ticker and short company name)
            if q_objects:
                filtered_content = (
                    Article.objects.filter(q_objects)
                    .select_related("source")
                    .exclude(source__in=selected_portfolio.blacklisted_sources.all())
                )
                portfolio_stocks = PortfolioStockSerializer(
                    stocks, many=True, context={"filtered_content": filtered_content}
                ).data
                filtered_content_list = list(filtered_content)
                (
                    analysis_content,
                    commentary_content,
                    news_content,
                ) = create_content_lists(filtered_content_list)
            else:
                analysis_content = commentary_content = news_content = (
                    Article.objects.none()
                )

        else:
            analysis_content = commentary_content = news_content = (
                Article.objects.none()
            )
            portfolio_stocks = None

        context["stocks"] = portfolio_stocks
        context["selected_portfolio"] = selected_portfolio
        context["user_portfolios"] = Portfolio.objects.filter(
            user=self.request.user
        ).order_by("name")
        context["analysis"] = create_paginator(
            self.request,
            analysis_content,
            25,
            "analysis",
        )
        context["commentary"] = create_paginator(
            self.request,
            commentary_content,
            25,
            "commentary",
        )
        context["news"] = create_paginator(
            self.request,
            news_content,
            25,
            "news",
        )
        return context


class PortfolioDetailView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View for displaying details of a user's stock portfolio.

    This view requires the user to be logged in and retrieves the specified
    portfolio by its ID. It fetches the stocks associated with the portfolio
    and filters relevant articles based on these stocks.
    """

    model = Portfolio
    context_object_name = "portfolio"
    template_name = "stock/portfolio.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves the context data for rendering the selected portfolio details.

        Args:
            **kwargs (Any): Additional keyword arguments passed to the method.

        Returns:
            Dict[str, Any]: Context data to be used in the template, including:
                - Stocks in the selected portfolio
                - Selected portfolio
                - All user portfolios
                - Filtered articles categorized by type (analysis, commentary, news)
        """
        context = super().get_context_data(**kwargs)
        selected_portfolio = get_object_or_404(
            Portfolio, portfolio_id=self.kwargs["portfolio_id"]
        )
        stocks = (
            PortfolioStock.objects.filter(portfolio=selected_portfolio)
            .select_related("stock")
            .prefetch_related("keywords", "portfolio")
            .order_by("stock__ticker")
        )

        # check if the portfolio has any stocks to avoid timeout errors
        if stocks.exists():
            q_objects = create_portfolio_search_object(stocks)

            # potential edge case only stock in portfolio (e.g. Bill which will lead to no english words because of english word in ticker and short company name)
            if q_objects:
                filtered_content = (
                    Article.objects.filter(q_objects)
                    .select_related("source")
                    .exclude(source__in=selected_portfolio.blacklisted_sources.all())
                )
                portfolio_stocks = PortfolioStockSerializer(
                    stocks, many=True, context={"filtered_content": filtered_content}
                ).data
                filtered_content_list = list(filtered_content)
                (
                    analysis_content,
                    commentary_content,
                    news_content,
                ) = create_content_lists(filtered_content_list)
            else:
                analysis_content = commentary_content = news_content = (
                    Article.objects.none()
                )

        else:
            analysis_content = commentary_content = news_content = (
                Article.objects.none()
            )
            portfolio_stocks = None

        context["stocks"] = portfolio_stocks
        context["selected_portfolio"] = selected_portfolio
        context["user_portfolios"] = Portfolio.objects.filter(
            user=self.request.user
        ).order_by("name")
        context["analysis"] = create_paginator(
            self.request,
            analysis_content,
            25,
            "analysis",
        )
        context["commentary"] = create_paginator(
            self.request,
            commentary_content,
            25,
            "commentary",
        )
        context["news"] = create_paginator(
            self.request,
            news_content,
            25,
            "news",
        )
        return context
