# Django imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from django.db.models import Count, F
# Python imports
from datetime import timedelta



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

def lists_filter(timeframe, content_type, minimum_rating, primary_source, lists):    
    if timeframe != "All":
        lists = lists.filter(updated_at__gte = now() - timedelta(days=int(timeframe)))
    if content_type != "All":
        if content_type == "Articles":
             lists = lists.annotate(list_articles=Count('articles', distinct=True), list_sources=Count('sources', distinct=True)).filter(list_articles__gt=F('list_sources'))
        else:
            lists = lists.annotate(list_sources=Count('sources', distinct=True), list_articles=Count('articles', distinct=True)).filter(list_sources__gt=F('list_articles'))
    exclude_list = []
    if minimum_rating != "All":
        minimum_rating = float(minimum_rating)
        for list in lists:
            if list.get_average_rating != "None":
                if list.get_average_rating < minimum_rating:
                    exclude_list.append(list)
            else:
                exclude_list.append(list)
    if len(exclude_list):
        for list in exclude_list:
            lists = lists.exclude(list_id=list.list_id)
    if primary_source != "All":
        lists = lists.filter(main_website_source = primary_source)
    return lists