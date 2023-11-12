# Django imports
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from researchbrowserproject.settings import STATIC_ROOT

# Python imports
import os

# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.source.models import Source
from apps.article.models import Article, TrendingTopicContent, StockPitch
from apps.stock.models import Stock
from apps.home.models import NotificationMessage

User = get_user_model()


class GuideView(TemplateView, BaseMixin):
    template_name = "home/guide.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        long_form = [
            "Net Interest",
            "Chartbook",
            "Doomberg",
            "Fabricated Knowledge - Substack",
            "Investi Analyst Newsletter",
            "Not Boring by Packy McCormick",
            "TSOH Investment Research Service",
            "Apricitas Economics",
            "Software Stack Investing",
            "Convequity - Substack",
        ]
        podcast = [
            "All-In Podcast",
            "Acquired",
            "Business Breakdowns",
            "Portfolio Matters",
            "Stratechery - Spotify",
            "The Town with Matthew Belloni",
            "Yet Another Value Channel",
            "Big Technology Podcast",
            "Invest Like the Best with Patrick O'Shaughnessy",
            "HC Insider",
        ]
        twitter = [
            "Rihard Jarc",
            "Internal Tech Emails",
            "Stream by AlphaSense",
            "Aswath Damodaran",
            "Francis - Analyst 🚢",
            "Forward Cap",
            "In Practise",
            "Walter Bloomberg",
            "Eric Seufert",
            "Holger Zschaepitz",
        ]
        industry_news_provider = [
            "TechCrunch",
            "The Business of Fashion",
            "TechNode",
            "American Banker",
            "Business Of Apps",
            "Retail TouchPoints",
            "Ecommerce Research & News",
            "Rest Of World",
            "Just Auto",
            "SpaceNews",
        ]
        insider = [
            "The Entertainment Strategy Guy",
            "OnlyCFO's Software World",
            "Technically",
            "SiliconANGLE theCUBE",
            "Americas Market Intelligence",
            "CarDealershipGuy - Twitter",
            "Boz To The Future",
            "HHHYPERGROWTH",
            "Deconstructor of Fun",
            "The Pragmatic Engineer - Substack",
        ]
        investment_fund = [
            "Meritech Capital",
            "Bison Interests",
            "ARK Invest",
            "Cedar Grove Capital",
            "Smoak Capital - Blog",
            "Sequoia Capital",
            "Distillate Capital",
            "Andreessen Horowitz",
            "Boyar Value Group",
            "Exploring with Alluvial Capital",
        ]
        financial_professionals = [
            "Mohamed A. El-Erian",
            "Gavin Baker",
            "Jamin Ball",
            "Freda Duan",
            "MacroPolo Econ",
            "Chinese Characteristics",
            "Below the Line from Kevin LaBuz",
            "Futurum Research",
            "IvanaSPEAR",
            "5 Points",
        ]
        tech = [
            "Platformer",
            "Bert Hochfeld",
            "Benedict Evans",
            "Tidal Wave",
            "Stock Market Nerd",
            "Stratechery - Blog",
            "Mostly Borrowed Ideas",
            "Punch Card Investor",
            "Tanay’s Newsletter",
            "Big Technology",
        ]
        semiconductor = [
            "Fabricated Knowledge - Substack",
            "SemiAnalysis",
            "Semi-Literate",
            "Asianometry",
            "Sravan Kundojjala",
            "Robert Castellano",
            "Semiconductor News by Dylan Martin",
            "Transistor Radio",
            "Dan Nystedt",
            "Dylan Patel",
        ]
        energy = [
            "Giovanni Staunovo🛢🇮🇹",
            "Doomberg",
            "WTI Realist’s Newsletter",
            "Stephen Stapczynski",
            "Commodity Context",
            "Super-Spiked",
            "Energy Investor's Research",
            "Energy Flux",
            "The Coal Trader",
            "HC Insider",
        ]
        macro = [
            "Sofia Horta e Costa",
            "Portfolio Matters",
            "Chartbook",
            "Apricitas Economics",
            "Alf",
            "Patrick Boyle",
            "Bond Blogger's Credit Wrap",
            "Lyn Alden - Blog",
            "Mohamed A. El-Erian",
            "Holger Zschaepitz",
        ]
        shorts = [
            "Hindenburg Research - Blog",
            "Muddy Waters Research - Blog",
            "Citron Research - Twitter",
            "Culper",
            "The Bear Cave",
            "NINGI Research",
            "Spruce Point Capital - Twitter",
            "Bleecker Street Research - Blog",
            "Viceroy Research - Blog",
            "Iceberg Research - Blog",
        ]
        fintech = [
            "Kunle.app",
            "Fintech Takes",
            "David Jiménez Maireles",
            "Fintech Brain Food 🧠",
            "Fintech Blueprint",
            "Popular Fintech",
            "Linas's Newsletter",
            "Fintech Across the Pond",
            "Fintech Business Weekly",
            "Fintech Inside",
        ]
        small_cap = [
            "Vestrule",
            "In the Ruff Research",
            "The Superinvestors of Augustusville",
            "Ian Cassel",
            "Investing501 Newsletter",
            "Under-Followed-Stocks",
            "Planet MicroCap Podcast",
            "ToffCap",
            "Hurdle Rate",
            "Jonah’s Deep Dives on Small/Mid Caps",
        ]
        geopolitics = [
            "Bismarck Brief",
            "CaspianReport",
            "Palladium",
            "Pekingnology",
            "The Eurasian Century",
            "Foreign Policy Research Institute",
            "Foreign Policy",
            "War on the Rocks",
            "Americas Quarterly",
            "Geopolitical Musings",
        ]
        context["long_form"] = Source.objects.filter(name__in=long_form).order_by(
            "name"
        )
        context["podcast"] = Source.objects.filter(name__in=podcast).order_by("name")
        context["twitter"] = Source.objects.filter(name__in=twitter).order_by("name")
        context["industry_news_provider"] = Source.objects.filter(
            name__in=industry_news_provider
        ).order_by("name")
        context["insider"] = Source.objects.filter(name__in=insider).order_by("name")
        context["investment_fund"] = Source.objects.filter(
            name__in=investment_fund
        ).order_by("name")
        context["financial_professionals"] = Source.objects.filter(
            name__in=financial_professionals
        ).order_by("name")
        context["tech"] = Source.objects.filter(name__in=tech).order_by("name")
        context["fintech"] = Source.objects.filter(name__in=fintech).order_by("name")
        context["small_cap"] = Source.objects.filter(name__in=small_cap).order_by(
            "name"
        )
        context["semiconductor"] = Source.objects.filter(
            name__in=semiconductor
        ).order_by("name")
        context["energy"] = Source.objects.filter(name__in=energy).order_by("name")
        context["macro"] = Source.objects.filter(name__in=macro).order_by("name")
        context["geopolitics"] = Source.objects.filter(name__in=geopolitics).order_by(
            "name"
        )
        context["shorts"] = Source.objects.filter(name__in=shorts).order_by("name")
        return context


class NotificationView(LoginRequiredMixin, TemplateView, BaseMixin):
    template_name = "home/notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            NotificationMessage.objects.filter(
                notification__user=self.request.user
            ).update(user_has_seen=True)
        return context


class NotFoundView(
    TemplateView, BaseMixin
):  # immer auf aktuellen Stand zu FeedView halten
    template_name = "home/feed.html"

    def get_context_data(self, **kwargs):
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
    template_name = "home/feed.html"

    def get_context_data(self, **kwargs):
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
    template_name = "home/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs["search_term"]
        context["filtered_stocks"] = Stock.objects.filter_by_search_term(search_term)
        context["filtered_sources"] = Source.objects.filter_by_search_term(search_term)
        filtered_content = Article.objects.filter_by_search_term(search_term)
        context["analysis"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Analysis"),
            50,
            "analysis",
        )
        context["commentary"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="Commentary"),
            50,
            "commentary",
        )
        context["news"] = paginator_create(
            self.request,
            filtered_content.filter(source__content_type="News"),
            50,
            "news",
        )
        return context


class FaviconView(View):
    def get(self, request, *args, **kwargs):
        favicon_path = os.path.join(STATIC_ROOT, "home/media/favicon.ico")
        if os.path.exists(favicon_path):
            with open(favicon_path, "rb") as f:
                favicon = f.read()
            return HttpResponse(favicon, content_type="image/x-icon")
        else:
            return HttpResponse(status=404)


def error_view_500(request):
    return render(request, "server_error.html", status=500)


def error_view_503(request):
    return render(request, "server_error.html", status=503)
