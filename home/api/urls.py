# Django imports
from django.urls import path
# Local imports
from home.api.api import (
    list_filter, FilteredList, FilteredSite, FilteredSource, get_list_filters,
    article_filter, get_article_filters, list_change_subscribtion_status,
    source_change_subscribtion_status, delete_source_from_list, delete_list,
    sources_add, source_rate, list_rate, article_highlight, lists_add_article,
    profile_add_website_link, profile_pic_delete)

app_name = 'api'

urlpatterns = [
    path('list_change_subscribtion_status/<int:list_id>/<str:action>',
         list_change_subscribtion_status),
    path('source_change_subscribtion_status/<str:domain>/<str:action>',
         source_change_subscribtion_status),
    path('filter_list/<str:timeframe>/<str:content_type>/<str:sources>',
         list_filter),
    path('search_sources/<int:list_id>/<str:search_term>',
         FilteredSource.as_view()),
    path('search_lists/<str:search_term>', FilteredList.as_view()),
    path('get_list_filters', get_list_filters),
    path('search_site/<str:search_term>', FilteredSite.as_view()),
    path(
        'filter_articles/<str:timeframe>/<str:sector>/<str:paywall>/<str:sources>',
        article_filter),
    path('get_article_filters', get_article_filters),
    path('delete_source_from_list/<int:list_id>/<str:source>',
         delete_source_from_list),
    path('delete_list/<int:list_id>', delete_list),
    path('add_sources/<str:sources>/<int:list_id>', sources_add),
    path('rate_source/<str:source>/<int:rating>', source_rate),
    path('rate_list/<int:list_id>/<int:rating>', list_rate),
    path('highlight_article/<int:article_id>/<str:action>', article_highlight),
    path('add_article_to_lists/<int:article_id>/<str:list_ids>',
         lists_add_article),
    path('profile_add_website_link/<str:website>/<str:link>',
         profile_add_website_link),
    path('delete_profile_pic', profile_pic_delete)
]