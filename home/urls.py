# Django imports
from unicodedata import name
from django.urls import path
# Local imports
from home.views import browser, lists, sectors, list_details
from home.api import (source_delete, category_add, category_delete,
                      category_change, list_filter, FilteredList,
                      get_list_filters)

app_name = 'home'

urlpatterns = [
    path('browser/', browser, name='home-browser'),
    path('lists/', lists, name="home-lists"),
    path('sectors/', sectors, name="home-sectors"),
    path('list/<int:list_id>', list_details, name="home-list_details"),
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
    path('get_list_filters', get_list_filters, name="get-list-filters")
]
