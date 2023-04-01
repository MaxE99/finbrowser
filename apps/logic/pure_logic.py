# Django imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Local imports
from apps.api.serializers import SourceSerializer, ArticleSerializer, StockSerializer


def paginator_create(request, queryset, objects_per_site, page_name="page"):
    paginator = Paginator(queryset, objects_per_site)
    page = request.GET.get(page_name)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects


def stocks_get_experts(filtered_content):
    sources_articles_written = {}
    for content in filtered_content:
        if content.source in sources_articles_written.keys():
            sources_articles_written[content.source] += 1
        else:
            sources_articles_written[content.source] = 1
    sorted_sources = dict(
        sorted(sources_articles_written.items(), key=lambda item: item[1], reverse=True)
    )
    analysis_sources = []
    commentary_sources = []
    news_sources = []
    for source in sorted_sources:
        if source.content_type == "Analysis" and len(analysis_sources) < 16:
            analysis_sources.append(source)
        elif source.content_type == "Commentary" and len(commentary_sources) < 16:
            commentary_sources.append(source)
        elif source.content_type == "News" and len(news_sources) < 16:
            news_sources.append(source)
    return [analysis_sources, commentary_sources, news_sources]


def balance_search_results(filtered_stocks, filtered_sources, filtered_articles):
    len_filtered_stocks = filtered_stocks.count()
    len_filtered_sources = filtered_sources.count()
    len_filtered_articles = filtered_articles.count()
    display_spots_stocks = 3 if len_filtered_stocks > 3 else len_filtered_stocks
    display_spots_sources = 3 if len_filtered_sources > 3 else len_filtered_sources
    display_spots_articles = 3 if len_filtered_articles > 3 else len_filtered_articles
    all_spots = display_spots_stocks + display_spots_sources + display_spots_articles
    all_spots_previous_iteration = 0
    while all_spots < 9:
        if len_filtered_stocks > 3:
            display_spots_stocks += 1
            all_spots += 1
        if len_filtered_sources > 3:
            display_spots_sources += 1
            all_spots += 1
        if len_filtered_articles > 3:
            display_spots_articles += 1
            all_spots += 1
        if all_spots_previous_iteration == all_spots:
            break
        all_spots_previous_iteration = all_spots
    stock_serializer = StockSerializer(
        filtered_stocks[0:display_spots_stocks], many=True
    )
    sources_serializer = SourceSerializer(
        filtered_sources[0:display_spots_sources], many=True
    )
    articles_serializer = ArticleSerializer(
        filtered_articles[0:display_spots_articles], many=True
    )
    return (
        stock_serializer,
        sources_serializer,
        articles_serializer,
    )
