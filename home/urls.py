# Django imports
from django.urls import path
# Local imports
from home.views import (feed, lists, sectors, list_details, main, articles,
                        search_results, sector_details, settings)
from home.api import (source_delete, category_add, category_delete,
                      category_change, list_filter, FilteredList, FilteredSite,
                      get_list_filters, article_filter, get_article_filters,
                      list_change_subscribtion_status,
                      source_change_subscribtion_status)

app_name = 'home'

urlpatterns = [
    path('feed/', feed, name='home-feed'),
    path('lists/', lists, name="home-lists"),
    path('sectors/', sectors, name="home-sectors"),
    path('articles/', articles, name="home-articles"),
    path('main/', main, name="home-main"),
    path('settings/', settings, name="home-settings"),
    path('list_change_subscribtion_status/<int:list_id>/<str:action>',
         list_change_subscribtion_status,
         name="home-list_change_subscribtion_status"),
    path('source_change_subscribtion_status/<str:domain>/<str:action>',
         source_change_subscribtion_status,
         name="home-source_change_subscribtion_status"),
    path('search_results/<str:search_term>',
         search_results,
         name="home-search_results"),
    path('list/<int:list_id>', list_details, name="home-list_details"),
    path('sector/<str:name>', sector_details, name="home-sector_details"),
    path('delete_source/<str:source>', source_delete, name='source-delete'),
    path('add_category/<str:category>', category_add, name='category-add'),
    path('delete_category/<str:category>',
         category_delete,
         name='category-delete'),
    path('change_category/<str:source>/<str:new_category>',
         category_change,
         name='category_change'),
    path('filter_list/<str:timeframe>/<str:content_type>/<str:sources>',
         list_filter,
         name='list-filter'),
    path('search_lists/<str:search_term>',
         FilteredList.as_view(),
         name="search-lists"),
    path('get_list_filters', get_list_filters, name="get-list-filters"),
    path('search_site/<str:search_term>',
         FilteredSite.as_view(),
         name="search-site"),
    path(
        'filter_articles/<str:timeframe>/<str:sector>/<str:paywall>/<str:sources>',
        article_filter,
        name="article-filter"),
    path('get_article_filters',
         get_article_filters,
         name="get_article_filters"),
]
