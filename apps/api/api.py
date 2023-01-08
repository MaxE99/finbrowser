# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
# Local imports
from apps.api.serializers import (List_Serializer, Stock_Serializer, SourceTag_Serializer, Article_Serializer, Source_Serializer, Profile_Serializer, HighlightedArticle_Serializer, SourceRating_Serializer, ListRating_Serializer, Notification_Serializer)
from apps.api.permissions import IsListCreator, IsUser
from apps.home.models import NotificationMessage, Notification
from apps.accounts.models import Profile
from apps.article.models import HighlightedArticle, Article
from apps.source.models import Source, SourceRating, SourceTag
from apps.list.models import List, ListRating
from apps.stock.models import Stock


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsUser]
    authentication_classes=[SessionAuthentication]
    queryset = Profile.objects.all()
    serializer_class = Profile_Serializer
    http_method_names = ["delete"]

    @action(detail=True, methods=['delete'])
    def profile_pic_delete(self, request, *args, **kwargs):
        self.get_object().profile_pic.delete()
        return Response("Profile picture has been deleted!")


class HighlightedArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes=[SessionAuthentication]
    queryset = HighlightedArticle.objects.all()
    serializer_class = HighlightedArticle_Serializer
    http_method_names = ["post"]

    def create(self, request):
        article = get_object_or_404(Article, article_id=request.data['article_id'])
        if HighlightedArticle.objects.filter(user=request.user, article=article).exists():
            HighlightedArticle.objects.get(user=request.user, article=article).delete()
            return Response("Article has been unhighlighted!")
        HighlightedArticle.objects.create(user=request.user, article=article)
        return Response("Article has been highlighted!")


class SourceRatingViewSet(viewsets.ModelViewSet):
    queryset = SourceRating.objects.all()
    serializer_class = SourceRating_Serializer    
    permission_classes = [IsAuthenticated]
    authentication_classes=[SessionAuthentication] 
    http_method_names = ["post"] 

    def create(self, request):
        source = get_object_or_404(Source, source_id=request.data['source_id'])
        rating = request.data['rating']
        if SourceRating.objects.filter(user=request.user, source=source).exists():
            rating_instance = SourceRating.objects.get(user=request.user, source=source)
            rating_instance.rating = rating
            rating_instance.save()
            return Response("Rating has been changed!")
        SourceRating.objects.create(user=request.user, source=source, rating=rating)
        return Response("Rating has been added!")


class ListRatingViewSet(viewsets.ModelViewSet):
    queryset = ListRating.objects.all()
    serializer_class = ListRating_Serializer    
    permission_classes = [IsAuthenticated]
    authentication_classes=[SessionAuthentication]  
    http_method_names = ["post"]

    def create(self, request):
        list = get_object_or_404(List, list_id=request.data['list_id'])
        rating = request.data['rating']
        if ListRating.objects.filter(user=request.user, list=list).exists():
            rating_instance = ListRating.objects.get(user=request.user, list=list)
            rating_instance.rating = rating
            rating_instance.save()
            return Response("Rating has been changed!")
        ListRating.objects.create(user=request.user, list=list, rating=rating)
        return Response("Rating has been added!")


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = Source_Serializer
    http_method_names = ["post", "get"]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        list_id = self.request.GET.get("list_id", None)
        list_search = self.request.GET.get('list_search', None)
        feed_search = self.request.GET.get('feed_search', None)
        sectors_search = self.request.GET.get('sectors_search', None)
        if list_search != None:
            list = get_object_or_404(List, list_id=list_id)
            if list.creator == self.request.user:   
                return Source.objects.filter_by_list_and_search_term_exclusive(list_search, list)[0:10]
            return None
        elif feed_search != None:   
            return Source.objects.filter_by_subscription_and_search_term_exclusive(feed_search, self.request.user)[0:10]
        elif sectors_search != None:   
            return Source.objects.filter(name__istartswith=sectors_search)[0:10]
        else:
            return Source.objects.all()

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated])
    def source_change_subscribtion_status(self, request, *args, **kwargs):
        source = self.get_object()
        if source.subscribers.filter(username=request.user.username).exists():
            source.subscribers.remove(request.user)
            return Response("Source has been unsubscribed!")
        source.subscribers.add(request.user.id)
        return Response("Source has been subscribed!")


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = List_Serializer
    http_method_names = ["post", "delete", "get"]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        feed_search = self.request.GET.get("feed_search", None)
        if feed_search != None:
            return List.objects.filter_by_search_term_and_subscription_status(feed_search, self.request.user)[0:10]
        return List.objects.all()

    def destroy(self, request, *args, **kwargs):
        if self.get_object().creator == request.user:
            self.get_object().delete()
            return Response("List has been deleted!")
        return Response("Access Denied")

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated])
    def list_change_subscribtion_status(self, request, *args, **kwargs):
        list = self.get_object()
        if list.subscribers.filter(username=request.user.username).exists():
            list.subscribers.remove(request.user)
            return Response("List subscription removed!")
        list.subscribers.add(request.user.id)
        return Response("List subscription added!")

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], url_path=r'delete_source_from_list/(?P<source_id>\d+)', permission_classes=[IsAuthenticated, IsListCreator])
    def delete_source_from_list(self, request, pk, source_id):
        list = self.get_object()
        if list.creator == request.user:
            source = get_object_or_404(Source, source_id=source_id)
            list.sources.remove(source)
            return Response("Source has been removed from the list!")
        return Response("Access Denied")

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], url_path=r'delete_article_from_list/(?P<article_id>\d+)', permission_classes=[IsAuthenticated, IsListCreator])
    def delete_article_from_list(self, request, pk, article_id):
        list = self.get_object()
        if list.creator == request.user:
            article = get_object_or_404(Article, article_id=article_id)
            list.articles.remove(article)
            return Response("Article has been removed from the list!")
        return Response("Access Denied")

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], url_path=r'add_article_to_list/(?P<article_id>\d+)', permission_classes=[IsAuthenticated])
    def add_article_to_list(self, request, pk, article_id):
        list = self.get_object()
        if list.creator == request.user:
            article = get_object_or_404(Article, article_id=article_id)
            list.articles.add(article)
            return Response("Article has been added to the list!")
        return Response("Access Denied")


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, ))
def change_source_status_from_lists(request):
    source = get_object_or_404(Source, source_id=request.data['source_id'])
    for list_id in request.data['add_lists']:
        list = get_object_or_404(List, list_id=list_id)
        if list.creator == request.user:
            list.sources.add(source)
        else:
            return Response("Access Denied")
    for list_id in request.data['remove_lists']:
        list = get_object_or_404(List, list_id=list_id)
        if list.creator == request.user:
            list.sources.remove(source)
        else:
            return Response("Access Denied")
    return Response("Lists have been updated!")


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, ))
def add_sources_to_list(request, list_id, source_ids):
    list = get_object_or_404(List, list_id=list_id)
    if list.creator == request.user:
        list.sources.add(*source_ids.split(","))
        return Response("List has been updated!")
    return Response("Access Denied") 


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, ))
def subscribe_to_sources(request, source_ids):
    for source_id in source_ids.split(","):
        source = get_object_or_404(Source, source_id=source_id)
        source.subscribers.add(request.user)
    return Response("List has been updated!")


class FilteredLists(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term, format=None):
        filtered_lists =  List.objects.filter_by_search_term(search_term)[0:10]
        list_urls = [list.get_absolute_url() for list in filtered_lists]
        serializer = List_Serializer(filtered_lists, many=True)
        return JsonResponse([serializer.data, list_urls], safe=False)


class FilteredArticles(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term, format=None):
        filtered_articles = Article.objects.filter_by_search_term(search_term)[0:10]
        serializer = Article_Serializer(filtered_articles, many=True)
        article_favicon_paths = list(filtered_articles.values_list("source__favicon_path", flat=True))
        return JsonResponse([serializer.data, article_favicon_paths], safe=False)


class FilteredSources(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term, format=None):
        filtered_sources = Source.objects.filter(name__istartswith=search_term)[0:10]
        serializer = Source_Serializer(filtered_sources, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredSite(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, search_term, format=None):
        filtered_stocks = Stock.objects.filter_by_search_term(search_term)
        filtered_sources = Source.objects.filter_by_search_term(search_term)
        filtered_articles = Article.objects.filter(search_vector=search_term).select_related('source')
        # rebalance spots that are displayed
        len_filtered_stocks = filtered_stocks.count()
        len_filtered_sources = filtered_sources.count()
        len_filtered_articles = filtered_articles.count()
        display_spots_stocks = 3 if len_filtered_stocks > 3 else len_filtered_stocks
        display_spots_sources = 3 if len_filtered_sources > 3 else len_filtered_sources
        display_spots_articles = 3 if len_filtered_articles > 3 else len_filtered_articles
        all_spots = display_spots_stocks + display_spots_sources + display_spots_articles
        all_spots_previous_iteration = 0
        while all_spots < 9:
            if len_filtered_stocks > 3:
                display_spots_stocks += 1
                all_spots += 1
            if len_filtered_sources > 3:
                display_spots_sources += 1
                all_spots += 1
            if len_filtered_articles > 3:
                display_spots_articles += 1
                all_spots += 1
            if all_spots_previous_iteration == all_spots:
                break
            all_spots_previous_iteration = all_spots
        article_favicon_paths = list(filtered_articles.values_list("source__favicon_path", flat=True)[0:10])
        stock_serializer = Stock_Serializer(filtered_stocks[0:display_spots_stocks], many=True)
        sources_serializer = Source_Serializer(filtered_sources[0:display_spots_sources], many=True)
        articles_serializer = Article_Serializer(filtered_articles[0:display_spots_articles], many=True)
        return JsonResponse([stock_serializer.data, sources_serializer.data, articles_serializer.data, article_favicon_paths], safe=False)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = Notification_Serializer    
    authentication_classes = [SessionAuthentication]

    def create(self, request):
        source_id = request.data.get('source_id', None)
        stock_id = request.data.get('stock_id', None)
        if source_id != None:
            source = get_object_or_404(Source, source_id=source_id)
            notification, created = Notification.objects.get_or_create(user=request.user, source=source)
        elif stock_id != None:
            stock = get_object_or_404(Stock, stock_id=stock_id)
            notification, created = Notification.objects.get_or_create(user=request.user, stock=stock)
        if created:
            return Response("Notification has been added!")
        notification.delete()
        return Response("Notification has been removed!")

    def put(self, request, *args, **kwargs):
        NotificationMessage.objects.filter(notification__user=request.user).update(user_has_seen=True)
        return Response("Notifications have been marked as seen!")


class SourceTagViewSet(viewsets.ModelViewSet):
    queryset = SourceTag.objects.all()
    serializer_class = SourceTag_Serializer
    http_method_names = ["get"]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        return SourceTag.objects.filter(name__istartswith=self.request.GET['search_term']).order_by("name")