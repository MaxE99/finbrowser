from django.urls import path
from support.views import (report_bug, suggestions,suggest_sources, FaqView, SitemapView, AboutView, TermsOfServiceView, CookieStatementView, PrivacyPolicyView)

app_name = 'support'

urlpatterns = [
    path('faq/', FaqView.as_view(), name='faq'),
    path('report-bug/', report_bug, name='report-bug'),
    path('suggestions/', suggestions, name='suggestions'),
    path('privacy-policy', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('cookie-statement', CookieStatementView.as_view(), name='cookie-statement'),
    path('terms-of-service', TermsOfServiceView.as_view(), name='terms-of-service'),
    path('suggest-sources', suggest_sources, name="suggest-sources"),
    path('about', AboutView.as_view(), name="about"),
    path('sitemap', SitemapView.as_view(), name="sitemap"),
]