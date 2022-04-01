# Django imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Python imports
from operator import attrgetter
# Local imports
from home.logic.services import article_create


def paginator_create(request, lists, lists_per_site):
    lists = sorted(lists, key=attrgetter('likes'), reverse=True)
    paginator = Paginator(lists, lists_per_site)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    return articles, page

def timeframe_check(timeframe, time_since_pub, articles, favicon, title, link,
                    pub_date):
    """Checks the timeframe that the user wants for his search and creates only articles
    that were published during this timeframe."""
    match timeframe:
        case "Last 24 Hours":
            search_timeframe = 1
        case "Last 7 Days":
            search_timeframe = 7
        case "Last 30 Days":
            search_timeframe = 30
        case "Last 365 Days":
            search_timeframe = 365
        case _:
            search_timeframe = False
    if time_since_pub.days < search_timeframe or search_timeframe is False:
            article_create(articles, favicon, title, link, pub_date)