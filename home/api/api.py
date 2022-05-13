# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
# Local imports
from home.models import Article, HighlightedArticle, Notification, Source, List, SourceRating, ListRating
from accounts.models import Profile, SocialLink, Website
from home.api.serializers import List_Serializer, Article_Serializer, Source_Serializer


@api_view(["POST"])
def profile_add_website_link(request, website, link):
    SocialLink.objects.create(profile=request.user.profile,
                              website=website,
                              url=link)
    return Response("Link has been added!")


@api_view(["POST"])
def lists_add_article(request, article_id, list_ids):
    # add that articles that are already part of the list are checked
    article = get_object_or_404(Article, article_id=article_id)
    List.objects.add_articles(article, list_ids)
    return Response("Article has been added to list!")


@api_view(['POST'])
def article_highlight(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    if HighlightedArticle.objects.filter(user=request.user,
                                         article=article).exists():
        HighlightedArticle.objects.get(user=request.user,
                                       article=article).delete()
        return Response(f'Article has been unhighlighted!')
    else:
        HighlightedArticle.objects.create(user=request.user, article=article)
        return Response(f'Article has been highlighted!')


@api_view(['POST'])
def list_change_subscribtion_status(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    if list.subscribers.filter(username=request.user.username).exists():
        list.subscribers.remove(request.user)
        return Response("List has been unsubscribed!")
    else:
        list.subscribers.add(request.user.id)
        return Response("List has been subscribed!")


@api_view(['POST'])
def source_change_subscribtion_status(request, domain):
    source = get_object_or_404(Source, domain=domain)
    if source.subscribers.filter(username=request.user.username).exists():
        source.subscribers.remove(request.user)
        return Response("Source has been unsubscribed!")
    else:
        source.subscribers.add(request.user.id)
        return Response("Source has been subscribed!")


@api_view(['POST'])
def sources_add(request, sources, list_id):
    list = get_object_or_404(List, list_id=list_id)
    Source.objects.add_sources_to_list(sources, list)
    return Response("Sources have been added!")


@api_view(['POST'])
def source_rate(request, source, rating):
    source = get_object_or_404(Source, domain=source)
    SourceRating.objects.save_rating(request.user, source, rating)
    return Response("Rating has been saved in the database")


@api_view(['POST'])
def list_rate(request, list_id, rating):
    list = get_object_or_404(List, list_id=list_id)
    ListRating.objects.save_rating(request.user, list, rating)
    return Response("Rating has been saved in the database")


@api_view(["POST"])
def social_links_add(request, website, url):
    website = get_object_or_404(Website, name=website)
    SocialLink.objects.create(profile=request.user.profile,
                              website=website,
                              url=url.replace('"', ""))
    return Response("Link has been created!")


@api_view(["POST"])
def social_link_change(request, website, new_link):
    website = get_object_or_404(Website, name=website)
    social_link = get_object_or_404(SocialLink,
                                    website=website,
                                    profile=request.user.profile)
    social_link.url = new_link.replace('"', "")
    social_link.save()
    return Response("Link has been changed!")


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


@api_view(['DELETE'])
def delete_source_from_list(request, list_id, source):
    list = get_object_or_404(List, list_id=list_id)
    source = get_object_or_404(Source, name=source)
    list.sources.remove(source.source_id)
    return Response("Source has been removed from list!")


@api_view(['DELETE'])
def delete_article_from_list(request, list_id, article_id):
    list = get_object_or_404(List, list_id=list_id)
    list.articles.remove(article_id)
    return Response("Article has been removed from list!")


@api_view(['DELETE'])
def delete_list(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    list.delete()
    return Response("List has been deleted!")


@api_view(['DELETE'])
def profile_pic_delete(request):
    get_object_or_404(Profile, user=request.user).profile_pic.delete()
    return Response("Profile picture has been deleted!")


@api_view(['DELETE'])
def profile_banner_delete(request):
    get_object_or_404(Profile, user=request.user).profile_banner.delete()
    return Response("Profile banner has been deleted!")


@api_view(['DELETE'])
def social_link_delete(request, website):
    website = get_object_or_404(Website, name=website)
    get_object_or_404(SocialLink,
                      profile=request.user.profile,
                      website=website).delete()
    return Response("Link has been deleted!")


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
