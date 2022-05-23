from django.urls import path
from support.views import (ReportBugView, FeatureSuggestionView, SourceSuggestionView, FaqView, SitemapView, AboutView, TermsOfServiceView, CookieStatementView, PrivacyPolicyView)

app_name = 'support'

urlpatterns = [
    path('faq/', FaqView.as_view(), name='faq'),
    path('report-bug/', ReportBugView.as_view(), name='report-bug'),
    path('suggestions/', FeatureSuggestionView.as_view(), name='suggestions'),
    path('privacy-policy', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('cookie-statement', CookieStatementView.as_view(), name='cookie-statement'),
    path('terms-of-service', TermsOfServiceView.as_view(), name='terms-of-service'),
    path('suggest-sources', SourceSuggestionView.as_view(), name="suggest-sources"),
    path('about', AboutView.as_view(), name="about"),
    path('sitemap', SitemapView.as_view(), name="sitemap"),
]