from django.urls import path
from support.views import (faq, report_bug, suggestions, privacy_policy,
                           cookie_statement, terms_of_service, suggest_sources,
                           about, sitemap)

app_name = 'support'

urlpatterns = [
    path('faq/', faq, name='faq'),
    path('report-bug/', report_bug, name='report-bug'),
    path('suggestions/', suggestions, name='suggestions'),
    path('privacy-policy', privacy_policy, name='privacy-policy'),
    path('cookie-statement', cookie_statement, name='cookie-statement'),
    path('terms-of-service', terms_of_service, name='terms-of-service'),
    path('suggest-sources', suggest_sources, name="suggest-sources"),
    path('about', about, name="about"),
    path('sitemap', sitemap, name="sitemap"),
]