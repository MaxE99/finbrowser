# Django imports
from django.urls import path
from rest_framework.routers import DefaultRouter
# Local imports
from home.views import browser, lists, sectors
from home.api import (source_delete, category_add, category_delete,
                      category_change, list_filter, ListViewSet)

app_name = 'home'

urlpatterns = [
    path('browser/', browser, name='home-browser'),
    path('lists/', lists, name="home-lists"),
    path('sectors/', sectors, name="home-sectors"),
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
]

router = DefaultRouter()
router.register("api/lists", ListViewSet, basename="lists")

urlpatterns += router.urls