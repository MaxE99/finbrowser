# Django imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
# Python imports
from datetime import timedelta

# class TestPaginator(Paginator):
    
#     @cached_property
#     def count(self):
#         return 10000


def paginator_create(request, queryset, objects_per_site, page_name='page'):
    paginator = Paginator(queryset, objects_per_site)
    page = request.GET.get(page_name)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects

# def lists_filter(timeframe, content_type, minimum_rating, primary_source, lists):    
#     if timeframe != "All":
#         lists = lists.filter(updated_at__gte = now() - timedelta(days=int(timeframe)))
#     if content_type != "All":
#         if content_type == "Articles":
#              lists = lists.annotate(list_articles=Count('articles', distinct=True), list_sources=Count('sources', distinct=True)).filter(list_articles__gt=F('list_sources'))
#         else:
#             lists = lists.annotate(list_sources=Count('sources', distinct=True), list_articles=Count('articles', distinct=True)).filter(list_sources__gt=F('list_articles'))
#     exclude_list = []
#     if minimum_rating != "All":
#         minimum_rating = float(minimum_rating)
#         for list in lists:
#             if list.average_rating != None:
#                 if list.average_rating < minimum_rating:
#                     exclude_list.append(list)
#             else:
#                 exclude_list.append(list)
#     if len(exclude_list):
#         for list in exclude_list:
#             lists = lists.exclude(list_id=list.list_id)
#     if primary_source != "All":
#         lists = lists.filter(main_website_source = primary_source)
#     return lists


def lists_filter(timeframe, content_type, minimum_rating, primary_source, lists):
    filter_args = {}
    if timeframe != 'All' and timeframe != None:
        filter_args['updated_at__gte'] = now()-timedelta(days=int(timeframe))
    if minimum_rating != 'All' and type != None:
        filter_args['average_rating__gte'] = float(minimum_rating)
    if primary_source != 'All' and type != None:
        filter_args['main_website_source'] = primary_source    
    lists = lists.filter(**filter_args).order_by('average_rating') 
    if content_type != "All":
            if content_type == "Articles":
                lists = lists.annotate(list_articles=Count('articles', distinct=True), list_sources=Count('sources', distinct=True)).filter(list_articles__gt=F('list_sources'))
            else:
                lists = lists.annotate(list_sources=Count('sources', distinct=True), list_articles=Count('articles', distinct=True)).filter(list_sources__gt=F('list_articles')) 
    return lists


def articles_filter(timeframe, sector, paywall, source, articles):
    filter_args = {'source__sector': sector, 'source__paywall': paywall, 'source__website': source}
    if timeframe != 'All' and timeframe != None:
        filter_args['pub_date__gte'] = now()-timedelta(days=int(timeframe))
    filter_args = dict((k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    return articles.filter(**filter_args).order_by('-pub_date')


def sources_filter(paywall, type, minimum_rating, website, sources):
    from apps.accounts.models import Website
    filter_args = {'paywall': paywall}
    if type != 'All' and type != None and type == "Analysis":
        filter_args['news'] = False
    elif type != 'All' and type != None and type == "News":
        filter_args['news'] = True
    if minimum_rating != 'All' and type != None:
        filter_args['average_rating__gte'] = float(minimum_rating)
    if website != 'All' and type != None:
        filter_args['website'] = get_object_or_404(Website, name=website)
    filter_args = dict((k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    return sources.filter(**filter_args)
