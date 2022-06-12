from django.urls import path
from support.views import (ReportBugView, FeatureSuggestionView, SourceSuggestionView, TermsOfServiceView, CookieStatementView, PrivacyPolicyView, ContactView)

app_name = 'support'

urlpatterns = [
    path('report-bug/', ReportBugView.as_view(), name='report-bug'),
    path('suggestions/', FeatureSuggestionView.as_view(), name='suggestions'),
    path('privacy-policy', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('cookie-statement', CookieStatementView.as_view(), name='cookie-statement'),
    path('terms-of-service', TermsOfServiceView.as_view(), name='terms-of-service'),
    path('suggest-sources', SourceSuggestionView.as_view(), name="suggest-sources"),
    path('contact', ContactView.as_view(), name="contact"),
]