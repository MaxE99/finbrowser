from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', views.faq, name='support-faq'),
    path('report_bug/', views.report_bug, name='support-report_bug'),
    path('suggestions/', views.suggestions, name='support-suggestions')
]