# Django imports
from django.urls import path
from django.views.decorators.cache import cache_page
# Local imports
from apps.main.views import MainView

app_name = 'main'

urlpatterns = [
    path('', cache_page(3600)(MainView.as_view()), name="main"),
]
