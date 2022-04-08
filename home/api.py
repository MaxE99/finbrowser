# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
# Local imports
from home.models import Article, BrowserSource, BrowserCategory, Source, List
from home.serializers import List_Serializer, Article_Serializer, Source_Serializer


@api_view(["DELETE"])
def category_delete(request, category):
    category = get_object_or_404(BrowserCategory, name=category)
    deleted_category = str(category)
    category.delete()
    return Response(f'"{deleted_category}" has been deleted')


@api_view(["DELETE"])
def source_delete(request, source):
    source = get_object_or_404(Source, domain=source)
    browser_source = get_object_or_404(BrowserSource, source=source)
    deleted_source = str(source)
    browser_source.delete()
    return Response(f'"{deleted_source}" has been deleted')


@api_view(["POST"])
def category_add(request, category):
    new_category = BrowserCategory(name=category)
    new_category.save()
    return Response(f'"{str(new_category)}" has been saved')


@api_view(["POST"])
def category_change(request, source, new_category):
    source = get_object_or_404(Source, domain=source)
    browser_source = get_object_or_404(BrowserSource, source=source)
    category = get_object_or_404(BrowserCategory, name=new_category)
    browser_source.category = category
    browser_source.save()
    return Response(
        f'"{str(source)}" has been added to category {new_category}')


@api_view(['POST'])
def list_change_subscribtion_status(request, list_id, action):
    list = get_object_or_404(List, list_id=list_id)
    if action == 'Subscribe':
        list.subscribers.add(request.user.id)
        return Response(f"You have subscribed to {list}")
    else:
        list.subscribers.remove(request.user)
        return Response(f"You have unsubscribed from {list}")


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


class FilteredList(APIView):

    def get(self, request, search_term, format=None):
        filtered_list = List.objects.filter(name__istartswith=search_term)[0:6]
        serializer = List_Serializer(filtered_list, many=True)
        return JsonResponse(serializer.data, safe=False)


class FilteredSite(APIView):

    def get(self, request, search_term, format=None):
        filtered_lists = List.objects.filter(
            name__istartswith=search_term)[0:3]
        list_serializer = List_Serializer(filtered_lists, many=True)
        filtered_sources = Source.objects.filter(
            domain__istartswith=search_term)[0:3]
        sources_serializer = Source_Serializer(filtered_sources, many=True)
        filtered_articles = Article.objects.filter(
            title__icontains=search_term)[0:3]
        articles_serializer = Article_Serializer(filtered_articles, many=True)
        return JsonResponse([
            list_serializer.data, sources_serializer.data,
            articles_serializer.data
        ],
                            safe=False)
