# Django imports
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.list.models import List
from apps.article.models import Article, HighlightedArticle
from apps.source.models import Source


User = get_user_model()


class HighlightedContentView(LoginRequiredMixin, TemplateView, BaseMixin):
    model = List
    context_object_name = "list"
    template_name = "list/highlighted_content_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["lists"] = List.objects.filter(creator=self.request.user)
            context["highlighted_content"] = paginator_create(
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
    model = List
    context_object_name = "list"
    template_name = "list/subscribed_sources_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            subscribed_sources = (
                Source.objects.filter_subscribed_sources_by_content_type(
                    self.request.user
                )
            )
            (
                analysis_content,
                commentary_content,
                news_content,
            ) = Article.objects.get_subscribed_content_by_content_type(
                subscribed_sources
            )
            context["lists"] = List.objects.filter(creator=self.request.user)
            context["analysis_sources"] = subscribed_sources["analysis"]
            context["commentary_sources"] = subscribed_sources["commentary"]
            context["news_sources"] = subscribed_sources["news"]
            context["analysis"] = paginator_create(
                self.request,
                analysis_content,
                25,
                "analysis",
            )
            context["commentary"] = paginator_create(
                self.request,
                commentary_content,
                25,
                "commentary",
            )
            context["news"] = paginator_create(
                self.request,
                news_content,
                25,
                "news",
            )
        return context


class ListDetailView(LoginRequiredMixin, TemplateView, BaseMixin):
    model = List
    context_object_name = "list"
    template_name = "list/list_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_list = get_object_or_404(List, list_id=self.kwargs["list_id"])
        context["lists"] = List.objects.filter(creator=self.request.user)
        context["list"] = selected_list
        context["saved_content"] = paginator_create(
            self.request,
            List.objects.get_highlighted_content(selected_list),
            25,
            "saved_content",
        )
        analysis, commentary, news = Article.objects.get_list_content_by_content_type(
            selected_list.sources.all()
        )
        context["analysis"] = paginator_create(self.request, analysis, 25, "analysis")
        context["commentary"] = paginator_create(
            self.request, commentary, 25, "commentary"
        )
        context["news"] = paginator_create(self.request, news, 25, "news")
        return context


class ListView(TemplateView, BaseMixin):
    model = List
    context_object_name = "list"
    template_name = "list/list_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context
        selected_list = get_object_or_404(
            List,
            creator=self.request.user,
            main=True,
        )
        context["lists"] = List.objects.filter(creator=self.request.user)
        context["list"] = selected_list
        context["saved_content"] = paginator_create(
            self.request,
            List.objects.get_highlighted_content(selected_list),
            25,
            "saved_content",
        )
        analysis, commentary, news = Article.objects.get_list_content_by_content_type(
            selected_list.sources.all()
        )
        context["analysis"] = paginator_create(self.request, analysis, 25, "analysis")
        context["commentary"] = paginator_create(
            self.request, commentary, 25, "commentary"
        )
        context["news"] = paginator_create(self.request, news, 25, "news")
        return context
