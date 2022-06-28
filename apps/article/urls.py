# Django imports
from django.urls import path
# Local imports
from apps.article.views import ArticleView, ArticleSearchView

app_name = 'article'

urlpatterns = [
    path('content/', ArticleView.as_view(), name="articles"),
    path('content/<str:timeframe>/<str:sector>/<str:paywall>/<str:source>/', ArticleSearchView.as_view(), name="articles-search"),
]
