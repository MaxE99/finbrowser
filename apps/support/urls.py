# Django imports
from django.urls import path
# Local imports
from apps.support.views import (ReportBugView, FeatureSuggestionView, SourceSuggestionView, TermsOfServiceView, CookieStatementView, PrivacyPolicyView, ContactView)

app_name = 'support'

urlpatterns = [
    path('support/report-bug/', ReportBugView.as_view(), name='report-bug'),
    path('support/suggestions/', FeatureSuggestionView.as_view(), name='suggestions'),
    path('support/privacy-policy', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('support/cookie-statement', CookieStatementView.as_view(), name='cookie-statement'),
    path('support/terms-of-service', TermsOfServiceView.as_view(), name='terms-of-service'),
    path('support/suggest-sources', SourceSuggestionView.as_view(), name="suggest-sources"),
    path('support/contact', ContactView.as_view(), name="contact"),
]
