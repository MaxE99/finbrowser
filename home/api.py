# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
# Local imports
from home.models import Article, Source, List, SourceRating, ListRating
from home.serializers import List_Serializer, Article_Serializer, Source_Serializer


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
    sources = sources.split(",")
    print(sources)
    for source in sources:
        source = get_object_or_404(Source, domain=source)
        list.sources.add(source)
    return Response("Sources have been added!")


@api_view(['POST'])
def source_rate(request, source, rating):
    source = get_object_or_404(Source, domain=source)
    if SourceRating.objects.filter(user=request.user, source=source).exists():
        source_rating = get_object_or_404(SourceRating,
                                          user=request.user,
                                          source=source)
        source_rating.rating = rating
        source_rating.save()
    else:
        SourceRating.objects.create(user=request.user,
                                    source=source,
                                    rating=rating)
    return Response("Rating has been saved in the database")


@api_view(['POST'])
def list_rate(request, list_id, rating):
    list = get_object_or_404(List, list_id=list_id)
    if ListRating.objects.filter(user=request.user, list=list).exists():
        list_rating = get_object_or_404(ListRating,
                                        user=request.user,
                                        list=list)
        list_rating.rating = rating
        list_rating.save()
    else:
        ListRating.objects.create(user=request.user, list=list, rating=rating)
    return Response("Rating has been saved in the database")


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
def delete_source_from_list(request, list_name, source):
    list = get_object_or_404(List, name=list_name)
    source = get_object_or_404(Source, name=source)
    list.sources.remove(source.source_id)
    return Response(f"{source} has been removed from {list_name}")


@api_view(['DELETE'])
def delete_list(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    list_name = str(list)
    list.delete()
    return Response(f"{list_name} has been deleted")


class FilteredSource(APIView):

    def get(self, request, list_id, search_term, format=None):
        list = get_object_or_404(List, list_id=list_id)
        filtered_sources = Source.objects.filter(
            name__istartswith=search_term).exclude(
                source_id__in=list.sources.all())[0:5]
        serializer = Source_Serializer(filtered_sources, many=True)
        return JsonResponse(serializer.data, safe=False)


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
