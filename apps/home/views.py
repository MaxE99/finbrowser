# Django imports
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.source.models import Source
from apps.article.models import Article, TrendingTopicContent
from apps.stock.models import Stock
from apps.home.models import NotificationMessage
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()


class GuideView(TemplateView, BaseMixin):
    template_name = "home/guide.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        the_best = [
            "Bert Hochfeld",
            "All-In Podcast",
            "Fabricated Knowledge - Substack",
            "Not Boring by Packy McCormick",
            "Software Stack Investing",
            "Stratechery",
            "*Walter Bloomberg",
            "Yet Another Value Channel",
            "Convequity - Substack",
            "Doomberg",
        ]
        long_form = [
            "Bert Hochfeld",
            "Convequity - Substack",
            "Doomberg",
            "Fabricated Knowledge - Substack",
            "Investi Analyst Newsletter",
            "Not Boring by Packy McCormick",
            "Palladium",
            "PETITION",
            "Software Stack Investing",
            "SemiAnalysis",
        ]
        podcast = [
            "All-In Podcast",
            "Acquired",
            "Business Breakdowns",
            "Portfolio Matters",
            "Stratechery",
            "The Razor's Edge",
            "Yet Another Value Channel",
            "Futurum Research",
            "Invest Like the Best with Patrick O'Shaughnessy",
            "HC Insider",
        ]
        twitter = [
            "David Jiménez Maireles",
            "Giulio S.",
            "Rihard Jarc",
            "Sravan Kundojjala",
            "WTCM",
            "Forward Cap",
            "In Practise",
            "*Walter Bloomberg",
            "Gianluca",
            "Holger Zschaepitz",
        ]
        energy = [
            "Giovanni Staunovo",
            "Doomberg",
            "Portfolio Matters",
            "Stephen Stapczynski",
            "Super-Spiked",
            "Javier Blas",
            "Criterion Research",
            "Fluidsdoc",
            "Long Player",
            "HC Insider",
        ]
        context["the_best"] = Source.objects.filter(name__in=the_best).order_by("name")
        context["long_form"] = Source.objects.filter(name__in=long_form).order_by(
            "name"
        )
        context["podcast"] = Source.objects.filter(name__in=podcast).order_by("name")
        context["twitter"] = Source.objects.filter(name__in=twitter).order_by("name")
        context["energy"] = Source.objects.filter(name__in=energy).order_by("name")
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
        # if self.request.user.is_authenticated:
        #     top_tweets = Article.objects.get_best_tweets_anon()
        #     recommended_content = Article.objects.get_top_content_anon()[0:10]
        # else:
        top_tweets = Article.objects.get_best_tweets_anon()
        recommended_content = Article.objects.get_top_content_anon()[0:25]
        context["top_tweets"] = top_tweets[0:25]
        context["latest_analysis"] = Article.objects.get_latest_analysis()
        context["latest_news"] = Article.objects.get_latest_news()
        context["trending_topics"] = TrendingTopicContent.objects.all().select_related(
            "article__source", "article__source__website"
        )[0:10]
        context["recommended_sources"] = Source.objects.get_random_top_sources()
        context["recommended_content"] = recommended_content
        context["error_page"] = True
        return context


class FeedView(TemplateView, BaseMixin):
    template_name = "home/feed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        #     top_tweets = Article.objects.get_best_tweets_anon()
        #     recommended_content = Article.objects.get_top_content_anon()[0:10]
        # else:
        top_tweets = Article.objects.get_best_tweets_anon()
        recommended_content = Article.objects.get_top_content_anon()[0:25]
        context["top_tweets"] = top_tweets[0:25]
        context["latest_analysis"] = Article.objects.get_latest_analysis()
        context["latest_news"] = Article.objects.get_latest_news()
        context["trending_topics"] = TrendingTopicContent.objects.all().select_related(
            "article__source", "article__source__website"
        )[0:10]
        context["recommended_sources"] = Source.objects.get_random_top_sources()
        context["recommended_content"] = recommended_content
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
