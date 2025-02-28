import os
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

from apps.utils import create_paginator
from apps.mixins import BaseMixin
from apps.source.models import Source
from apps.article.models import Article, TrendingTopicContent, StockPitch
from apps.stock.models import Stock
from apps.home.models import NotificationMessage
from data.guide_sources import sources_dict
from researchbrowserproject.settings import STATIC_URL


User = get_user_model()


class GuideView(TemplateView, BaseMixin):
    """
    A view that displays a guide with categorized sources.

    This view inherits from TemplateView and BaseMixin and renders a template
    containing various categories of sources such as long-form articles,
    podcasts, and industry news providers. It retrieves these sources from
    the database based on predefined lists in `sources_dict`.
    """

    template_name = "home/guide.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieve context data for the guide template.

        This method adds various categories of sources to the context,
        querying the database for each category listed in `sources_dict`.

        Args:
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Dict[str, Any]: A dictionary containing context data for the template,
            including categorized sources.
        """
        context = super().get_context_data(**kwargs)
        context["long_form"] = Source.objects.filter(
            name__in=sources_dict["long_form"]
        ).order_by("name")
        context["podcast"] = Source.objects.filter(
            name__in=sources_dict["podcast"]
        ).order_by("name")
        context["insider"] = Source.objects.filter(
            name__in=sources_dict["insider"]
        ).order_by("name")
        context["investment_fund"] = Source.objects.filter(
            name__in=sources_dict["investment_fund"]
        ).order_by("name")
        context["financial_professionals"] = Source.objects.filter(
            name__in=sources_dict["financial_professionals"]
        ).order_by("name")
        context["tech"] = Source.objects.filter(name__in=sources_dict["tech"]).order_by(
            "name"
        )
        context["fintech"] = Source.objects.filter(
            name__in=sources_dict["fintech"]
        ).order_by("name")
        context["small_cap"] = Source.objects.filter(
            name__in=sources_dict["small_cap"]
        ).order_by("name")
        context["semiconductor"] = Source.objects.filter(
            name__in=sources_dict["semiconductor"]
        ).order_by("name")
        context["energy"] = Source.objects.filter(
            name__in=sources_dict["energy"]
        ).order_by("name")
        context["macro"] = Source.objects.filter(
            name__in=sources_dict["macro"]
        ).order_by("name")
        context["geopolitics"] = Source.objects.filter(
            name__in=sources_dict["geopolitics"]
        ).order_by("name")
        context["cloudfront_dist"] = STATIC_URL
        return context


class NotificationView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View for displaying user notifications.

    This view handles the display of notifications for authenticated users.
    It marks all notifications as seen when accessed.
    """

    template_name = "home/notifications.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds notification data to the context.

        Args:
            **kwargs: Additional context arguments.

        Returns:
            A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            NotificationMessage.objects.filter(
                notification__user=self.request.user
            ).update(user_has_seen=True)
        return context


class NotFoundView(
    TemplateView, BaseMixin
):  # immer auf aktuellen Stand zu FeedView halten
    """
    View for displaying the not found (404) page.

    This view provides content for the 404 error page, including
    the latest articles, trending topics, and recommended sources.
    """

    template_name = "home/feed.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds error page data to the context.

        Args:
            **kwargs: Additional context arguments.

        Returns:
            A dictionary containing the context data, including
            error flags and recommended content.
        """
        context = super().get_context_data(**kwargs)
        context["error_page"] = True
        context["latest_analysis"] = Article.objects.get_latest_analysis()
        context["latest_news"] = Article.objects.get_latest_news()
        context["trending_topics"] = (
            TrendingTopicContent.objects.all()
            .order_by("-article__pub_date")
            .select_related("article__source", "article__source__website")[0:10]
        )
        context["stock_pitches"] = (
            StockPitch.objects.all()
            .order_by("-article__pub_date")
            .select_related("article__source", "article__source__website")[0:10]
        )
        context["recommended_sources"] = Source.objects.get_random_top_sources()
        context["recommended_content"] = Article.objects.get_top_content_anon()[0:25]
        return context


class FeedView(TemplateView, BaseMixin):
    """
    View for displaying the main feed.

    This view provides the main feed of content, including
    the latest articles, trending topics, and recommended sources.
    """

    template_name = "home/feed.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds feed data to the context.

        Args:
            **kwargs: Additional context arguments.

        Returns:
            A dictionary containing the context data, including
            latest articles and recommended content.
        """
        context = super().get_context_data(**kwargs)
        context["latest_analysis"] = Article.objects.get_latest_analysis()
        context["latest_news"] = Article.objects.get_latest_news()
        context["trending_topics"] = (
            TrendingTopicContent.objects.all()
            .order_by("-article__pub_date")
            .select_related("article__source", "article__source__website")[0:10]
        )
        context["stock_pitches"] = (
            StockPitch.objects.all()
            .order_by("-article__pub_date")
            .select_related("article__source", "article__source__website")[0:10]
        )
        context["recommended_sources"] = Source.objects.get_random_top_sources()
        context["recommended_content"] = Article.objects.get_top_content_anon()[0:25]
        return context


class SearchResultView(TemplateView, BaseMixin):
    """
    View for displaying search results.

    This view displays the search results for stocks, sources, and articles
    based on the user's search term.
    """

    template_name = "home/search_results.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds search result data to the context.

        Args:
            **kwargs: Additional context arguments.

        Returns:
            A dictionary containing the context data, including
            filtered stocks, sources, and paginated articles.
        """
        context = super().get_context_data(**kwargs)
        search_term = kwargs["search_term"]
        filtered_content = Article.objects.filter_by_search_term(search_term)

        context["filtered_stocks"] = Stock.objects.filter_by_search_term(search_term)
        context["filtered_sources"] = Source.objects.filter_by_search_term(search_term)
        context["analysis"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            50,
            "analysis",
        )
        context["commentary"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            50,
            "commentary",
        )
        context["news"] = create_paginator(
            self.request,
            filtered_content.filter(source__content_type="News"),
            50,
            "news",
        )
        return context


class FaviconView(View):
    """
    View for serving the favicon.

    This view retrieves and serves the favicon file from the static files.
    """

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handles GET requests to serve the favicon.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An HttpResponse with the favicon file or a 404 status if not found.
        """
        favicon_path = os.path.join(STATIC_URL, "home/media/favicon.ico")

        if os.path.exists(favicon_path):
            with open(favicon_path, "rb") as f:
                favicon = f.read()

            return HttpResponse(favicon, content_type="image/x-icon")

        else:
            return HttpResponse(status=404)


def error_view_500(request: HttpRequest) -> HttpResponse:
    """
    Custom 500 error view.

    Renders the server error page for 500 errors.

    Args:
        request: The HTTP request.

    Returns:
        An HttpResponse rendering the server error page with a status of 500.
    """
    return render(request, "server_error.html", status=500)


def error_view_503(request: HttpRequest) -> HttpResponse:
    """
    Custom 503 error view.

    Renders the server error page for 503 errors.

    Args:
        request: The HTTP request.

    Returns:
        An HttpResponse rendering the server error page with a status of 503.
    """
    return render(request, "server_error.html", status=503)
