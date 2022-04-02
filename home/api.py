# Django imports
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
# Local imports
from home.models import BrowserSource, BrowserCategory, Source, List
from home.serializers import List_Serializer


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


@api_view(['GET'])
def list_filter(request, timeframe, content_type, sources):
    cache.set_many({
        'timeframe': timeframe,
        'content_type': content_type,
        'sources': sources
    })
    return Response("Lists have been filtered!")


@api_view(['GET'])
def get_list_filters(request):
    timeframe = cache.get('timeframe')
    content_type = cache.get('content_type')
    sources = cache.get('sources')
    return Response([timeframe, content_type, sources])


class FilteredList(APIView):

    def get(self, request, search_term, format=None):
        filtered_list = List.objects.filter(name__istartswith=search_term)[0:6]
        serializer = List_Serializer(filtered_list, many=True)
        return JsonResponse(serializer.data, safe=False)
