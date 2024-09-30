from typing import Any

from django.http import HttpResponse, Http404
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import Profile
from apps.article.models import Article, HighlightedArticle
from apps.api.permissions import (
    IsListCreator,
    IsUser,
    IsPortfolioCreator,
    PortfolioKeywordPermission,
)
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
from apps.api.utils import balance_search_results, get_amount_portfolio_search_terms
from apps.home.models import Notification, NotificationMessage
from apps.list.models import List
from apps.source.models import Source, SourceRating, SourceTag
from apps.stock.models import Portfolio, PortfolioKeyword, PortfolioStock, Stock


class ListViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing user's lists. It allows the user to create, update, and delete lists.

    The deletion method ensures that a user cannot delete their last list and will auto-assign
    a new main list if the main list is deleted.
    """

    queryset = List.objects.all()
    serializer_class = ListSerializer
    http_method_names = ["post", "patch", "delete"]
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsListCreator]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Deletes a list object if conditions are met. Ensures the user can't delete their last list.
        If the main list is being deleted, another list will be assigned as the main one.

        Args:
            request (Request): The HTTP request object, containing user and data information.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments (including 'pk' for the list id).

        Returns:
            Response: A success message upon deletion, or an error response if deletion is not allowed.
        """
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
    """
    A viewset for managing source objects. This allows users to retrieve and update
    source objects based on specific query parameters for list search, blacklist search,
    and subscription search.
    """

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    http_method_names = ["get", "patch"]
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self) -> models.QuerySet:
        """
        Returns a filtered queryset based on the request parameters: `list_search`,
        `blacklist_search`, or `subs_search`. If no specific search parameter is provided,
        returns all sources.

        - For `list_search`: Filters by a list owned by the requesting user.
        - For `blacklist_search`: Filters by sources not blacklisted in the user's portfolio.
        - For `subs_search`: Filters by sources not subscribed by the user.

        Raises:
            Http404: If the provided list or portfolio ID is not found or not owned by the current user.

        Returns:
            QuerySet: A filtered queryset based on the search parameters.
        """
        list_search = self.request.GET.get("list_search")
        blacklist_search = self.request.GET.get("blacklist_search")
        subs_search = self.request.GET.get("subs_search")

        if list_search:
            selected_list = get_object_or_404(
                List, list_id=self.request.GET.get("list_id")
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
    """
    A viewset for managing user profiles. This viewset allows users to update their own profile
    information using a PATCH request.
    """

    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    http_method_names = ["patch"]


class SourceRatingViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing source ratings. This viewset allows users to rate sources using
    a POST request to create a new rating.
    """

    queryset = SourceRating.objects.all()
    serializer_class = SourceRatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    http_method_names = ["post"]


class HighlightedArticleViewSet(viewsets.ModelViewSet):
    """
    A viewset for highlighting or un-highlighting articles for a user. The user can
    highlight an article by making a POST request, and the same request will un-highlight
    the article if it's already highlighted.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    queryset = HighlightedArticle.objects.all()
    serializer_class = HighlightedArticleSerializer
    http_method_names = ["post"]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Toggles the highlighted state of an article for the current user.

        If the article is already highlighted, it will be unhighlighted. Otherwise, it will be highlighted.

        Args:
            request (Request): The HTTP request object, containing the article to highlight/unhighlight.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: A message indicating whether the article was highlighted or unhighlighted.
        """
        article = get_object_or_404(Article, article_id=request.data["article"])
        highlighted_article = HighlightedArticle.objects.filter(
            user=request.user, article=article
        )

        if highlighted_article.exists():
            highlighted_article.delete()
            return Response(
                "Article has been unhighlighted!", status=status.HTTP_200_OK
            )

        HighlightedArticle.objects.create(user=request.user, article=article)
        return Response("Article has been highlighted!", status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing notifications. It allows marking notifications as seen
    or deleting them.
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    http_method_names = ["put", "post", "delete"]

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Marks all notifications related to the current user as seen.

        Args:
            request (Request): The HTTP request object, containing user data.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: A message confirming that notifications have been marked as seen.
        """
        NotificationMessage.objects.filter(notification__user=request.user).update(
            user_has_seen=True
        )
        return Response(
            "Notifications have been marked as seen!", status=status.HTTP_200_OK
        )


class SourceTagViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing source tags. It allows retrieving tags based on a search term.
    """

    queryset = SourceTag.objects.all()
    serializer_class = SourceTagSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self) -> models.QuerySet:
        """
        Retrieves source tags based on a search term provided via GET parameters.

        Returns:
            QuerySet: A queryset of SourceTag objects filtered by the search term.
        """
        search_term = self.request.GET.get("search_term", "")
        return SourceTag.objects.filter(name__istartswith=search_term).order_by("name")


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing user portfolios. It allows users to create, update, and delete portfolios,
    ensuring that they cannot delete their last remaining portfolio. If the main portfolio is deleted,
    another portfolio is assigned as the new main portfolio.
    """

    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes = [SessionAuthentication]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    http_method_names = ["post", "patch", "delete"]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Deletes a portfolio, ensuring the user cannot delete their last portfolio.
        If the main portfolio is deleted, another portfolio is marked as the main portfolio.

        Args:
            request (Request): The HTTP request object, containing user and data information.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments (including 'pk' for the portfolio ID).

        Returns:
            Response: A success message upon deletion, or an error response if deletion is not allowed.
        """
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
    """
    A viewset for retrieving stocks. It supports searching stocks based on a
    search term provided via GET parameters.
    """

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        """
        Retrieves a filtered queryset of stocks based on the search term provided via GET parameters.

        If a 'search_term' is present in the request's GET parameters, the queryset is filtered
        by the search term, otherwise it returns the default queryset.

        Returns:
            QuerySet: A filtered or default queryset of Stock objects.
        """
        search_term = self.request.GET.get("search_term")

        if search_term:
            return Stock.objects.filter_by_search_term_search(search_term, 25)

        return super().get_queryset()


class PortfolioStockViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing PortfolioStock objects, allowing users to add or delete stocks
    from their portfolios. It supports GET, POST, and DELETE HTTP methods.
    """

    permission_classes = [IsAuthenticated, IsPortfolioCreator]
    authentication_classes = [SessionAuthentication]
    queryset = PortfolioStock.objects.all()
    serializer_class = PortfolioStockSerializer
    http_method_names = ["get", "post", "delete"]

    def get_object(self):
        """
        Retrieve a PortfolioStock object based on the primary key (pk) provided in the URL.

        Returns:
            PortfolioStock: The PortfolioStock object matching the provided pk.
        """
        queryset = self.filter_queryset(self.get_queryset())
        return queryset.get(pk=self.kwargs["pk"])

    def create(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Create PortfolioStock objects for the given portfolio and stock(s). Checks for search term limits
        before allowing creation.

        Args:
            request (Request): The HTTP request containing the portfolio and stock information.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            HttpResponse: A response indicating the result of the creation process.
        """
        portfolio_id = request.data.get("portfolios") or request.data.get("portfolio")
        selected_portfolio = get_object_or_404(
            Portfolio, portfolio_id=portfolio_id, user=request.user
        )

        search_terms = get_amount_portfolio_search_terms(selected_portfolio)

        # Handle case when multiple portfolios are specified
        if request.data.get("portfolios"):
            if search_terms > 99:
                return HttpResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    content="You have already created the maximum number of objects allowed.",
                )
            PortfolioStock.objects.create(
                portfolio=selected_portfolio,
                stock=get_object_or_404(Stock, stock_id=request.data.get("stock_id")),
            )

        # Handle case for a single portfolio with multiple stocks
        else:
            stocks = request.data.get("stocks", [])
            if search_terms + len(stocks) > 100:
                return HttpResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    content="You have already created the maximum number of objects allowed.",
                )

            for stock_id in stocks:
                PortfolioStock.objects.create(
                    stock=get_object_or_404(Stock, stock_id=stock_id),
                    portfolio=get_object_or_404(
                        Portfolio,
                        portfolio_id=request.data.get("portfolio"),
                        user=request.user,
                    ),
                )

        return HttpResponse(status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated, IsPortfolioCreator))
@authentication_classes((SessionAuthentication,))
def remove_stock_from_portfolio(
    request, portfolio_id: str, stock_id: str
) -> HttpResponse:
    """
    Remove a stock from the specified portfolio if the authenticated user is the portfolio creator.

    Args:
        request (Request): The HTTP request object.
        portfolio_id (str): The ID of the portfolio.
        stock_id (str): The ID of the stock to remove.

    Returns:
        HttpResponse: A response with status 204 if the stock is successfully deleted.
    """
    portfolio = get_object_or_404(
        Portfolio, portfolio_id=portfolio_id, user=request.user
    )
    stock = get_object_or_404(Stock, stock_id=stock_id)

    portfolio_stock = get_object_or_404(
        PortfolioStock, portfolio=portfolio, stock=stock
    )
    portfolio_stock.delete()

    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


class PortfolioKeywordViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing PortfolioKeyword objects, allowing creation and deletion of portfolio keywords.
    """

    permission_classes = [IsAuthenticated, PortfolioKeywordPermission]
    authentication_classes = [SessionAuthentication]
    queryset = PortfolioKeyword.objects.all()
    serializer_class = PortfolioKeywordSerializer
    http_method_names = ["post", "delete"]


class FilteredSite(APIView):
    """
    An API view for retrieving filtered results for stocks, sources, and articles
    based on a search term provided via URL.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term: str) -> Response:
        """
        Retrieve filtered search results for stocks, sources, and articles based on a search term.

        Args:
            request (Request): The HTTP request object.
            search_term (str): The search term to filter stocks, sources, and articles.

        Returns:
            Response: response containing serialized stock, source, and article data.
        """
        filtered_stocks = Stock.objects.filter_by_search_term_search(search_term, 9)
        filtered_sources = Source.objects.filter_by_search_term(search_term)[:9]
        filtered_articles = Article.objects.filter(
            search_vector=search_term
        ).select_related("source")[:9]

        balanced_results = balance_search_results(
            filtered_stocks, filtered_sources, filtered_articles
        )

        return Response(
            {
                "stocks": balanced_results["stock_serializer"].data,
                "sources": balanced_results["sources_serializer"].data,
                "articles": balanced_results["articles_serializer"].data,
            }
        )


class ArticleViewSet(viewsets.ModelViewSet):
    """
    A viewset for retrieving articles. Supports filtering articles based on
    various criteria, such as top content, best tweets, and stock pitches.
    """

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    http_method_names = ["get"]

    def get_queryset(self) -> models.QuerySet:
        """
        Retrieves a filtered queryset of articles based on query parameters in the GET request.

        The request may include parameters such as 'feed_content', 'best_tweets', or 'stock_pitches'
        to filter the articles.

        Returns:
            QuerySet: A filtered or default queryset of Article objects.
        """

        if self.request.GET.get("feed_content"):
            position = int(self.request.GET.get("feed_content"))
            return Article.objects.get_top_content_anon()[position : position + 25]

        if self.request.GET.get("best_tweets"):
            position = int(self.request.GET.get("best_tweets"))
            return Article.objects.get_best_tweets_anon()[position : position + 25]

        if self.request.GET.get("stock_pitches"):
            position = int(self.request.GET.get("stock_pitches"))
            return Article.objects.get_stock_pitches()[position : position + 25]

        return super().get_queryset()
