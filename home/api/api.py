# Django imports
import re
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from accounts.views import profile
from home.api import serializers
from home.logic.scrapper import source_data_get
# Local imports
from home.models import Article, HighlightedArticle, Notification, Source, List, SourceRating, ListRating
from accounts.models import Profile, SocialLink, Website
from home.api.serializers import (List_Serializer, Article_Serializer, Source_Serializer, Profile_Serializer, HighlightedArticle_Serializer, SocialLink_Serializer, SourceRating_Serializer, ListRating_Serializer)
from home.api.permissions import IsListCreator, IsUser


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = List_Serializer

    def destroy(self, request, *args, **kwargs):
        list = self.get_object()
        if list.creator == request.user:
            self.get_object().delete()
            return Response("List has been deleted!")
        else:
            return Response("Access Denied")

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated])
    def list_change_subscribtion_status(self, request, *args, **kwargs):
        list = self.get_object()
        if list.subscribers.filter(username=request.user.username).exists():
            list.subscribers.remove(request.user)
            return Response("List has been unsubscribed!")
        else:
            list.subscribers.add(request.user.id)
            return Response("List has been subscribed!")

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], url_path=r'delete_source_from_list/(?P<source_id>\d+)', permission_classes=[IsAuthenticated, IsListCreator])
    def delete_source_from_list(self, request, pk, source_id):
        list = self.get_object()
        source = get_object_or_404(Source, source_id=source_id)
        list.sources.remove(source)
        return Response("Source has been removed from list!")

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], url_path=r'delete_article_from_list/(?P<article_id>\d+)', permission_classes=[IsAuthenticated, IsListCreator])
    def delete_article_from_list(self, request, pk, article_id):
        list = self.get_object()
        article = get_object_or_404(Article, article_id=article_id)
        list.articles.remove(article)
        return Response("Article has been removed from list!")

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], url_path=r'add_source/(?P<source_id>\d+)', permission_classes=[IsAuthenticated, IsListCreator])
    def add_source(self, request, pk, source_id):
        list = self.get_object()
        source = get_object_or_404(Source, source_id=source_id)
        list.sources.add(source)
        return Response("Source has been added to list!")

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], url_path=r'add_article_to_list/(?P<article_id>\d+)', permission_classes=[IsAuthenticated])
    def add_article_to_list(self, request, pk, article_id):
        list = self.get_object()
        article = get_object_or_404(Article, article_id=article_id)
        list.articles.add(article)
        return Response("Article has been added to list!")



# @api_view(["POST"])
# def list_change_article_status(request, article_id, lists_status):
#     article = get_object_or_404(Article, article_id=article_id)
#     lists_status = lists_status.split(",")
#     user_lists = List.objects.get_created_lists(request.user)
#     for i in range(len(lists_status)):
#         if lists_status[i] == "True":
#             if article not in user_lists[i].articles.all():
#                 user_lists[i].articles.add(article)
#         else:
#             if article in user_lists[i].articles.all():
#                 user_lists[i].articles.remove(article)
#     return Response("Lists have been changed!")



class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = Source_Serializer

    @action(detail=True, methods=['post'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated])
    def source_change_subscribtion_status(self, request, *args, **kwargs):
        source = self.get_object()
        if source.subscribers.filter(username=request.user.username).exists():
            source.subscribers.remove(request.user)
            return Response("Source has been unsubscribed!")
        else:
            source.subscribers.add(request.user.id)
            return Response("Source has been subscribed!")


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = Profile_Serializer

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated, IsUser])
    def profile_pic_delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.profile_pic.delete()
        return Response("Profile picture has been deleted!")

    @action(detail=True, methods=['delete'], authentication_classes=[SessionAuthentication], permission_classes=[IsAuthenticated, IsUser])
    def profile_banner_delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.profile_banner.delete()
        return Response("Profile banner has been deleted!")


class HighlightedArticleViewSet(viewsets.ModelViewSet):
    queryset = HighlightedArticle.objects.all()
    serializer_class = HighlightedArticle_Serializer

    def create(self, request):
        article_id = request.data['article_id']
        article = get_object_or_404(Article, article_id=article_id)
        if HighlightedArticle.objects.filter(user=request.user, article=article).exists():
            highlighted_article = HighlightedArticle.objects.get(user=request.user, article=article)
            highlighted_article.delete()
            return Response("Article has been unhighlighted!")
        else:
            HighlightedArticle.objects.create(user=request.user, article=article)
            return Response("Article has been highlighted!")


class SocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLink_Serializer    

    def create(self, request):
        website = request.data['website']
        website = get_object_or_404(Website, id=website)
        url = request.data['url']
        profile = request.user.profile
        SocialLink.objects.create(website=website, url=url, profile=profile)
        return Response("Link has been added!")

    def update(self, request, pk):
        social_link = self.get_object()
        if social_link.profile.user == request.user:
            website = request.data['website']
            website = get_object_or_404(Website, id=website)
            url = request.data['url']
            social_link.url = url
            social_link.save()
            return Response("Link has been changed!")
        else:
            return Response("Access Denied")

    def destroy(self, request, *args, **kwargs):
        social_link = self.get_object()
        if social_link.profile.user == request.user:
            social_link.delete()
            return Response("Link has been deleted!")
        else:
            return Response("Access Denied")


class SourceRatingViewSet(viewsets.ModelViewSet):
    queryset = SourceRating.objects.all()
    serializer_class = SourceRating_Serializer    

    def create(self, request):
        source_id = request.data['source_id']
        source = get_object_or_404(Source, source_id=source_id)
        rating = request.data['rating']
        if SourceRating.objects.filter(user=request.user, source=source).exists():
            rating_instance = SourceRating.objects.get(user=request.user, source=source)
            rating_instance.rating = rating
            rating_instance.save()
            return Response("Rating has been changed!")
        else:
            SourceRating.objects.create(user=request.user, source=source, rating=rating)
            return Response("Rating has been added!")


class ListRatingViewSet(viewsets.ModelViewSet):
    queryset = ListRating.objects.all()
    serializer_class = ListRating_Serializer    

    def create(self, request):
        list_id = request.data['list_id']
        list = get_object_or_404(List, list_id=list_id)
        rating = request.data['rating']
        if ListRating.objects.filter(user=request.user, list=list).exists():
            rating_instance = ListRating.objects.get(user=request.user, list=list)
            rating_instance.rating = rating
            rating_instance.save()
            return Response("Rating has been changed!")
        else:
            ListRating.objects.create(user=request.user, list=list, rating=rating)
            return Response("Rating has been added!")


class FilteredSourceForLists(APIView):

    def get(self, request, list_id, search_term, format=None):
        list = get_object_or_404(List, list_id=list_id)
        # special filter case as sources that are already in list are removed
        filtered_sources = Source.objects.filter_sources_not_in_list(
            search_term, list)[0:5]
        serializer = Source_Serializer(filtered_sources, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredSourceForFeed(APIView):

    def get(self, request, search_term):
        filtered_sources = Source.objects.filter_sources_not_subscribed(
            search_term, request.user)
        serializer = Source_Serializer(filtered_sources, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredListForFeed(APIView):

    def get(self, request, search_term):
        filtered_lists = List.objects.filter_lists_not_subscribed(
            search_term, request.user)
        serializer = List_Serializer(filtered_lists, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredSource(APIView):

    def get(self, request, search_term, format=None):
        filtered_sources = Source.objects.filter_sources(search_term)[0:6]
        serializer = Source_Serializer(filtered_sources, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredList(APIView):

    def get(self, request, search_term, format=None):
        filtered_list = List.objects.filter_lists(search_term)[0:6]
        serializer = List_Serializer(filtered_list, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredArticles(APIView):

    def get(self, request, search_term, format=None):
        filtered_articles = Article.objects.filter_articles(search_term)[0:6]
        serializer = Article_Serializer(filtered_articles, many=True)
        article_favicon_paths = []
        for article in filtered_articles:
            article_favicon_paths.append(article.source.favicon_path)
        return JsonResponse([serializer.data, article_favicon_paths],
                            safe=False)


class FilteredSite(APIView):

    def get(self, request, search_term, format=None):
        filtered_lists = List.objects.filter_lists(search_term)
        filtered_sources = Source.objects.filter_sources(search_term)
        filtered_articles = Article.objects.filter_articles(search_term)
        # rebalance spots that are displayed
        display_spots_lists = 3
        display_spots_sources = 3
        display_spots_articles = 3
        len_filtered_lists = len(filtered_lists)
        len_filtered_sources = len(filtered_sources)
        len_filtered_articles = len(filtered_articles)
        if len_filtered_lists < 3:
            display_spots_lists = len(filtered_lists)
        if len_filtered_sources < 3:
            display_spots_sources = len_filtered_sources
        if len_filtered_articles < 3:
            display_spots_articles = len_filtered_articles
        all_spots = display_spots_lists + display_spots_sources + display_spots_articles
        iteration = 1 + 3
        all_spots_previous_iteration = 0
        while all_spots < 9:
            if len_filtered_lists > iteration:
                display_spots_lists += 1
                all_spots += 1
            if len_filtered_sources > iteration:
                display_spots_sources += 1
                all_spots += 1
            if len_filtered_articles > iteration:
                display_spots_articles += 1
                all_spots += 1
            if all_spots_previous_iteration == all_spots:
                break
            all_spots_previous_iteration = all_spots
        article_favicon_paths = []
        for article in filtered_articles:
            article_favicon_paths.append(article.source.favicon_path)
        list_serializer = List_Serializer(
            filtered_lists[0:display_spots_lists], many=True)
        sources_serializer = Source_Serializer(
            filtered_sources[0:display_spots_sources], many=True)
        articles_serializer = Article_Serializer(
            filtered_articles[0:display_spots_articles], many=True)
        return JsonResponse([
            list_serializer.data, sources_serializer.data,
            articles_serializer.data, article_favicon_paths
        ],
                            safe=False)


@api_view(["POST"])
def notification_change_source(request, source_id):
    source = get_object_or_404(Source, source_id=source_id)
    notification, created = Notification.objects.get_or_create(
        user=request.user, source=source)
    if created:
        return Response("Notification has been added!")
    else:
        notification.delete()
        return Response("Notification has been removed!")


@api_view(["POST"])
def notification_change_list(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    notification, created = Notification.objects.get_or_create(
        user=request.user, list=list)
    if created:
        return Response("Notification has been added!")
    else:
        notification.delete()
        return Response("Notification has been removed!")