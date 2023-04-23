# Django imports
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.http import Http404


# Local imports
from apps.api.serializers import (
    ListSerializer,
    StockSerializer,
    SourceTagSerializer,
    SourceSerializer,
    ProfileSerializer,
    HighlightedArticleSerializer,
    SourceRatingSerializer,
    NotificationSerializer,
    PortfolioSerializer,
    PortfolioStockSerializer,
    PortfolioKeywordSerializer,
    ArticleSerializer,
)
from apps.api.permissions import (
    IsUser,
    IsListCreator,
    IsPortfolioCreator,
    PortfolioKeywordPermission,
)
from apps.home.models import NotificationMessage, Notification
from apps.accounts.models import Profile
from apps.article.models import HighlightedArticle, Article
from apps.source.models import Source, SourceRating, SourceTag
from apps.list.models import List
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword
from apps.logic.pure_logic import balance_search_results


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    http_method_names = ["post", "patch", "delete"]
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsListCreator]

    def destroy(self, request, *args, **kwargs):
        user_lists = List.objects.filter(creator=request.user)
        if user_lists.count() > 1:
            selected_list = get_object_or_404(List, list_id=kwargs.get("pk"))
            if selected_list.main:
                new_main_list = user_lists.exclude(main=True).first()
                new_main_list.main = True
                new_main_list.save()
            return super().destroy(request, *args, **kwargs)
        return Response(
            data="You are not allowed to delete your last list!",
            status=status.HTTP_400_BAD_REQUEST,
        )


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    http_method_names = ["get", "patch"]
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        list_search = self.request.GET.get("list_search", None)
        blacklist_search = self.request.GET.get("blacklist_search", None)
        subs_search = self.request.GET.get("subs_search", None)
        if list_search:
            selected_list = get_object_or_404(
                List, list_id=self.request.GET.get("list_id", None)
            )
            if selected_list.creator == self.request.user:
                return Source.objects.filter_by_list_and_search_term_exclusive(
                    list_search, selected_list
                )[0:10]
            raise Http404(
                "Could not find a list with that ID owned by the current user"
            )
        if blacklist_search:
            portfolio = get_object_or_404(
                Portfolio, portfolio_id=self.request.GET.get("portfolio_id")
            )
            if portfolio.user == self.request.user:
                return Source.objects.filter(
                    name__istartswith=blacklist_search
                ).exclude(
                    source_id__in=portfolio.blacklisted_sources.values_list(
                        "source_id", flat=True
                    )
                )[
                    0:10
                ]
            raise Http404(
                "Could not find a list with that ID owned by the current user"
            )
        if subs_search:
            subscribed_sources = Source.objects.filter_by_subscription(
                self.request.user
            )
            return Source.objects.filter(name__istartswith=subs_search).exclude(
                source_id__in=subscribed_sources
            )[:10]
        return Source.objects.all()


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    http_method_names = ["patch"]


class SourceRatingViewSet(viewsets.ModelViewSet):
    queryset = SourceRating.objects.all()
    serializer_class = SourceRatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    http_method_names = ["post"]


class HighlightedArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    queryset = HighlightedArticle.objects.all()
    serializer_class = HighlightedArticleSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        article = get_object_or_404(Article, article_id=request.data["article"])
        if HighlightedArticle.objects.filter(
            user=request.user, article=article
        ).exists():
            HighlightedArticle.objects.get(user=request.user, article=article).delete()
            return Response("Article has been unhighlighted!")
        HighlightedArticle.objects.create(user=request.user, article=article)
        return Response("Article has been highlighted!")


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    http_method_names = ["put", "post", "delete"]

    def put(self, request, *args, **kwargs):
        NotificationMessage.objects.filter(notification__user=request.user).update(
            user_has_seen=True
        )
        return Response("Notifications have been marked as seen!")


class SourceTagViewSet(viewsets.ModelViewSet):
    queryset = SourceTag.objects.all()
    serializer_class = SourceTagSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self):
        return SourceTag.objects.filter(
            name__istartswith=self.request.GET["search_term"]
        ).order_by("name")


class PortfolioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    http_method_names = ["post", "patch", "delete"]

    def destroy(self, request, *args, **kwargs):
        user_portfolios = Portfolio.objects.filter(user=request.user)
        if user_portfolios.count() > 1:
            selected_portfolio = get_object_or_404(
                Portfolio, portfolio_id=kwargs.get("pk")
            )
            if selected_portfolio.main:
                new_main_portfolio = user_portfolios.exclude(main=True).first()
                new_main_portfolio.main = True
                new_main_portfolio.save()
            return super().destroy(request, *args, **kwargs)
        return Response(
            data="You are not allowed to delete your last portfolio!",
            status=status.HTTP_400_BAD_REQUEST,
        )


class StockViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.GET.get("search_term"):
            search_term = self.request.GET.get("search_term")
            return Stock.objects.filter(
                Q(ticker__istartswith=search_term)
                | Q(search_vector=search_term)
                | Q(short_company_name__istartswith=search_term)
            )[:25]
        return super().get_queryset()


class PortfolioStockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsPortfolioCreator]
    authentication_classes = [SessionAuthentication]
    queryset = PortfolioStock.objects.all()
    serializer_class = PortfolioStockSerializer
    http_method_names = ["get", "post", "delete"]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.kwargs["pk"])
        return obj

    def create(self, request, *args, **kwargs):
        if request.data.get("portfolios"):
            print("if")
            for portfolio_id in request.data.get("portfolios"):
                print("portfolio_id")
                print(portfolio_id)
                print("user")
                print(request.user)
                print("portfolio")
                print(
                    get_object_or_404(
                        Portfolio, portfolio_id=portfolio_id, user=request.user
                    )
                )
                print(request.data.get("stock_id"))
                print("stock")
                print(
                    stock=get_object_or_404(
                        Stock, stock_id=request.data.get("stock_id")
                    )
                )
                selected_portfolio = get_object_or_404(
                    Portfolio, portfolio_id=portfolio_id, user=request.user
                )
                PortfolioStock.objects.create(
                    portfolio=selected_portfolio,
                    stock=get_object_or_404(
                        Stock, stock_id=request.data.get("stock_id")
                    ),
                )
        else:
            for stock_id in request.data.get("stocks"):
                PortfolioStock.objects.create(
                    stock=get_object_or_404(Stock, stock_id=stock_id),
                    portfolio=get_object_or_404(
                        Portfolio,
                        portfolio_id=request.data.get("portfolio"),
                        user=request.user,
                    ),
                )
        return HttpResponse(status=201)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated, IsPortfolioCreator))
@authentication_classes((SessionAuthentication,))
def remove_stock_from_portfolio(request, portfolio_id, stock_id):
    get_object_or_404(
        PortfolioStock,
        portfolio=get_object_or_404(
            Portfolio, portfolio_id=portfolio_id, user=request.user
        ),
        stock=get_object_or_404(Stock, stock_id=stock_id),
    ).delete()
    return HttpResponse(status=204)


class PortfolioKeywordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PortfolioKeywordPermission]
    authentication_classes = [SessionAuthentication]
    queryset = PortfolioKeyword.objects.all()
    serializer_class = PortfolioKeywordSerializer
    http_method_names = ["post", "delete"]


class FilteredSite(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term):
        filtered_stocks = Stock.objects.filter_by_search_term(search_term)
        filtered_sources = Source.objects.filter_by_search_term(search_term)
        filtered_articles = Article.objects.filter(
            search_vector=search_term
        ).select_related("source")
        (
            stock_serializer,
            sources_serializer,
            articles_serializer,
        ) = balance_search_results(filtered_stocks, filtered_sources, filtered_articles)
        return JsonResponse(
            [
                stock_serializer.data,
                sources_serializer.data,
                articles_serializer.data,
            ],
            safe=False,
        )


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.GET.get("feed_content"):
            position = int(self.request.GET.get("feed_content"))
            return Article.objects.get_top_content_anon()[position : position + 25]
        if self.request.GET.get("best_tweets"):
            position = int(self.request.GET.get("best_tweets"))
            return Article.objects.get_best_tweets_anon()[position : position + 25]
        return super().get_queryset()
