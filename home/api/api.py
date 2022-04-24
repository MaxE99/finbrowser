# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
# Local imports
from home.models import Article, ExternalArticle, HighlightedArticle, Notification, Source, List, SourceRating, ListRating
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
    return Response(f'{article} has been added to lists')


@api_view(['POST'])
def article_highlight(request, article_id, action):
    article = get_object_or_404(Article, article_id=article_id)
    if action == "highlight":
        HighlightedArticle.objects.create(user=request.user, article=article)
        return Response(f'{article.title} has been highlighted')
    else:
        HighlightedArticle.objects.get(user=request.user,
                                       article=article).delete()
        return Response(f'{article.title} has been unhighlighted')


@api_view(['POST'])
def list_change_subscribtion_status(request, list_id, action):
    list = get_object_or_404(List, list_id=list_id)
    if action == 'Subscribe':
        list.subscribers.add(request.user.id)
        return Response(f"You have subscribed to {list}")
    else:
        list.subscribers.remove(request.user)
        return Response(f"You have unsubscribed from {list}")


@api_view(['POST'])
def source_change_subscribtion_status(request, domain, action):
    source = get_object_or_404(Source, domain=domain)
    if action == 'Subscribe':
        source.subscribers.add(request.user.id)
        return Response(f"You have subscribed to {source}")
    else:
        source.subscribers.remove(request.user)
        return Response(f"You have unsubscribed from {source}")


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


@api_view(['GET'])
def list_filter(request, timeframe, content_type, sources):
    cache.set_many({
        'timeframe': timeframe,
        'content_type': content_type,
        'sources': sources
    })
    return Response("Lists have been filtered!")


@api_view(['GET'])
def article_filter(request, timeframe, sector, paywall, sources):
    cache.set_many({
        'articles_timeframe': timeframe,
        'articles_sector': sector,
        'articles_paywall': paywall,
        'articles_sources': sources
    })
    return Response("Lists have been filtered!")


@api_view(['GET'])
def get_list_filters(request):
    timeframe = cache.get('timeframe')
    content_type = cache.get('content_type')
    sources = cache.get('sources')
    return Response([timeframe, content_type, sources])


@api_view(['GET'])
def get_article_filters(request):
    timeframe = cache.get('articles_timeframe')
    sector = cache.get('articles_sector')
    paywall = cache.get('articles_paywall')
    sources = cache.get('articles_sources')
    return Response([timeframe, sector, paywall, sources])


@api_view(['DELETE'])
def delete_source_from_list(request, list_id, source):
    print("AUFGRUFEN")
    list = get_object_or_404(List, list_id=list_id)
    print("list durchlaufen")
    print(list)
    source = get_object_or_404(Source, name=source)
    list.sources.remove(source.source_id)
    return Response(f"{source} has been removed from {list}")


@api_view(['DELETE'])
def delete_list(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    list_name = str(list)
    list.delete()
    return Response(f"{list_name} has been deleted")


@api_view(['DELETE'])
def profile_pic_delete(request):
    get_object_or_404(Profile, user=request.user).profile_pic.delete()
    return Response("You're profile picture has been deleted!")


@api_view(['DELETE'])
def profile_banner_delete(request):
    get_object_or_404(Profile, user=request.user).profile_banner.delete()
    return Response("You're profile banner has been deleted!")


@api_view(['DELETE'])
def social_link_delete(request, website):
    website = get_object_or_404(Website, name=website)
    get_object_or_404(SocialLink,
                      profile=request.user.profile,
                      website=website).delete()
    return Response("Link has been deleted!")


@api_view(["DELETE"])
def external_article_delete(request, external_article_id):
    get_object_or_404(ExternalArticle, article_id=external_article_id).delete()
    return Response("External article has been deleted!")


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


class FilteredSite(APIView):

    def get(self, request, search_term, format=None):
        filtered_lists = List.objects.filter_lists(search_term)[0:3]
        list_serializer = List_Serializer(filtered_lists, many=True)
        filtered_sources = Source.objects.filter_sources(search_term)[0:3]
        sources_serializer = Source_Serializer(filtered_sources, many=True)
        filtered_articles = Article.objects.filter_articles(search_term)[0:3]
        articles_serializer = Article_Serializer(filtered_articles, many=True)
        article_favicon_paths = []
        for article in filtered_articles:
            article_favicon_paths.append(article.source.favicon_path)
        return JsonResponse([
            list_serializer.data, sources_serializer.data,
            articles_serializer.data, article_favicon_paths
        ],
                            safe=False)
