from typing import Any, Dict

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.utils import create_paginator
from apps.mixins import BaseMixin
from apps.list.models import List
from apps.article.models import Article, HighlightedArticle
from apps.source.models import Source


User = get_user_model()


class HighlightedContentView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View to display highlighted content for the authenticated user.

    This view fetches highlighted articles related to the user and displays them
    with pagination. Only available to authenticated users.
    """

    model = List
    context_object_name = "list"
    template_name = "list/highlighted_content_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves context data for the highlighted content view.

        Returns:
            Dict[str, Any]: The context data containing lists and highlighted articles
            related to the authenticated user.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["lists"] = List.objects.filter(creator=self.request.user)
            context["highlighted_content"] = create_paginator(
                self.request,
                HighlightedArticle.objects.filter(user=self.request.user)
                .select_related(
                    "article__source", "article__source__website", "article__tweet_type"
                )
                .order_by("-article__pub_date"),
                25,
                "page",
            )
        return context


class SubscribedSourcesView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View to display subscribed sources and categorized content for the authenticated user.

    This view fetches sources and content (analysis, commentary, news) subscribed by the user,
    and applies pagination.
    """

    model = List
    context_object_name = "list"
    template_name = "list/subscribed_sources_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves context data for the subscribed sources view.

        Returns:
            Dict[str, Any]: The context data containing lists, subscribed sources,
            and categorized content (analysis, commentary, news).
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            subscribed_sources = (
                Source.objects.filter_subscribed_sources_by_content_type(
                    self.request.user
                )
            )
            subscribed_content = Article.objects.get_subscribed_content_by_content_type(
                subscribed_sources
            )

            context["lists"] = List.objects.filter(creator=self.request.user)
            context["analysis_sources"] = subscribed_sources["analysis"]
            context["commentary_sources"] = subscribed_sources["commentary"]
            context["news_sources"] = subscribed_sources["news"]
            context["analysis"] = create_paginator(
                self.request,
                subscribed_content["analysis"],
                25,
                "analysis",
            )
            context["commentary"] = create_paginator(
                self.request,
                subscribed_content["commentary"],
                25,
                "commentary",
            )
            context["news"] = create_paginator(
                self.request,
                subscribed_content["news"],
                25,
                "news",
            )
        return context


class ListDetailView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View to display detailed information about a specific list for the authenticated user.

    The view fetches saved content, articles categorized by content type, and applies pagination.
    """

    model = List
    context_object_name = "list"
    template_name = "list/list_details.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves context data for the list detail view.

        Returns:
            Dict[str, Any]: The context data containing the selected list, saved content,
            and categorized articles (analysis, commentary, news).
        """
        context = super().get_context_data(**kwargs)
        selected_list = get_object_or_404(List, list_id=self.kwargs["list_id"])
        content = Article.objects.get_list_content_by_content_type(
            selected_list.sources.all()
        )

        context["lists"] = List.objects.filter(creator=self.request.user)
        context["list"] = selected_list
        context["saved_content"] = create_paginator(
            self.request,
            List.objects.get_highlighted_content(selected_list),
            25,
            "saved_content",
        )
        context["analysis"] = create_paginator(
            self.request, content["analysis"], 25, "analysis"
        )
        context["commentary"] = create_paginator(
            self.request, content["commentary"], 25, "commentary"
        )
        context["news"] = create_paginator(self.request, content["news"], 25, "news")
        return context


class ListView(TemplateView, BaseMixin):
    """
    View to display the main list for the authenticated user.

    The view retrieves the user's main list, saved content, and articles categorized
    by content type, and applies pagination.
    """

    model = List
    context_object_name = "list"
    template_name = "list/list_details.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves context data for the main list view.

        Returns:
            Dict[str, Any]: The context data containing the main list, saved content,
            and categorized articles (analysis, commentary, news).
        """
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context

        selected_list = get_object_or_404(
            List,
            creator=self.request.user,
            main=True,
        )
        content = Article.objects.get_list_content_by_content_type(
            selected_list.sources.all()
        )

        context["lists"] = List.objects.filter(creator=self.request.user)
        context["list"] = selected_list
        context["saved_content"] = create_paginator(
            self.request,
            List.objects.get_highlighted_content(selected_list),
            25,
            "saved_content",
        )
        context["analysis"] = create_paginator(
            self.request, content["analysis"], 25, "analysis"
        )
        context["commentary"] = create_paginator(
            self.request, content["commentary"], 25, "commentary"
        )
        context["news"] = create_paginator(self.request, content["news"], 25, "news")
        return context
