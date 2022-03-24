# Django imports
from django.urls import path
# Local imports
from home.views import browser, lists
from home.api import (source_delete, category_add, category_delete,
                      category_change)

app_name = 'home'

urlpatterns = [
    path('browser/', browser, name='home-browser'),
    path('lists/', lists, name="home-lists"),
    path('delete_source/<str:source>', source_delete, name='source-delete'),
    path('add_category/<str:category>', category_add, name='category-add'),
    path('delete_category/<str:category>',
         category_delete,
         name='category-delete'),
    path('change_category/<str:source>/<str:new_category>',
         category_change,
         name='category_change'),
]