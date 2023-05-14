# Django import
from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


# Local import
from apps.scrapper.english_words import english_words
from apps.logic.pure_logic import paginator_create, stocks_get_experts
from apps.home.views import BaseMixin
from apps.stock.models import Stock, Portfolio, PortfolioStock
from apps.article.models import Article
from apps.home.models import Notification
from apps.stock.serializers import PortfolioStockSerializer, PortfolioSerializer


class StockDetailView(DetailView, BaseMixin):
    model = Stock
    context_object_name = "stock"
    template_name = "stock/stock_details.html"

    def get_object(self, queryset=None):
        slug_with_point = self.kwargs["slug_with_point"]
        return get_object_or_404(Stock, ticker=slug_with_point)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock = self.get_object()
        if self.request.user.is_authenticated:
            context["portfolios"] = PortfolioSerializer(
                Portfolio.objects.filter(user=self.request.user).order_by("name"),
                many=True,
            ).data
            context[
                "notification_id"
            ] = Notification.objects.check_stock_notification_exists(
                self.request.user, stock
            )
        filtered_content = Article.objects.get_content_about_stock(stock)
        analysis_sources, commentary_sources, news_sources = stocks_get_experts(
            filtered_content
        )
        context["analysis_sources"] = analysis_sources
        context["commentary_sources"] = commentary_sources
        context["news_sources"] = news_sources
        context["analysis"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            25,
            "analysis",
        )
        context["commentary"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            25,
            "commentary",
        )
        context["news"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="News"),
            25,
            "news",
        )
        return context


class PortfolioView(TemplateView, BaseMixin):
    template_name = "stock/portfolio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context
        selected_portfolio = get_object_or_404(
            Portfolio, user=self.request.user, main=True
        )
        stocks = (
            PortfolioStock.objects.filter(portfolio=selected_portfolio)
            .select_related("stock", "portfolio")
            .prefetch_related("keywords")
            .order_by("stock__ticker")
        )
        q_objects = Q()
        for stock in stocks:
            if (
                len(stock.stock.ticker) > 1
                and stock.stock.ticker.lower() not in english_words
            ):
                q_objects.add(Q(search_vector=stock.stock.ticker), Q.OR)
            else:
                q_objects.add(Q(search_vector=f"${stock.stock.ticker}"), Q.OR)
            q_objects.add(Q(search_vector=stock.stock.short_company_name), Q.OR)
            for keyword in stock.keywords.all():
                q_objects.add(Q(search_vector=keyword.keyword), Q.OR)
        filtered_content = Article.objects.filter(q_objects).exclude(
            source__in=selected_portfolio.blacklisted_sources.all()
        )
        portfolio_stocks = PortfolioStockSerializer(
            stocks, many=True, context={"filtered_content": filtered_content}
        ).data
        context["stocks"] = portfolio_stocks
        context["selected_portfolio"] = selected_portfolio
        context["user_portfolios"] = Portfolio.objects.filter(user=self.request.user)
        context["analysis"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            25,
            "analysis",
        )
        context["commentary"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            25,
            "commentary",
        )
        context["news"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="News"),
            25,
            "news",
        )
        return context


class PortfolioDetailView(LoginRequiredMixin, TemplateView, BaseMixin):
    model = Portfolio
    context_object_name = "portfolio"
    template_name = "stock/portfolio.html"

    def get_context_data(self, **kwargs):
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
        portfolio_stocks = PortfolioStockSerializer(stocks, many=True).data
        filtered_content = Article.objects.get_portfolio_content(portfolio_stocks)
        context["stocks"] = portfolio_stocks
        context["selected_portfolio"] = selected_portfolio
        context["user_portfolios"] = Portfolio.objects.filter(user=self.request.user)
        context["analysis"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            25,
            "analysis",
        )
        context["commentary"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            25,
            "commentary",
        )
        context["news"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="News"),
            25,
            "news",
        )
        return context
