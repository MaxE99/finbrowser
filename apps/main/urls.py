# Django imports
from django.urls import path
# Local imports
from apps.main.views import MainView

app_name = 'main'

urlpatterns = [
    path('', MainView.as_view(), name="main"),
]
