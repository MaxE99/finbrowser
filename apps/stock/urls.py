# Django imports
from django.urls import path
# Local imports
from apps.stock.views import StockDetailView

app_name = 'stock'

urlpatterns = [
    path('stock/<slug:slug>', StockDetailView.as_view(), name='stock-details'),
]
