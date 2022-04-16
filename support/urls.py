from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', views.faq, name='faq'),
    path('report_bug/', views.report_bug, name='report-bug'),
    path('suggestions/', views.suggestions, name='suggestions')
]