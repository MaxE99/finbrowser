# Django imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Local imports

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
