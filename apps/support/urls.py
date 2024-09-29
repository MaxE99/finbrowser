from django.urls import path

from apps.support.views import (
    TermsOfServiceView,
    CookieStatementView,
    PrivacyPolicyView,
    ContactView,
)

app_name = "support"

urlpatterns = [
    path("support/privacy-policy", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path(
        "support/cookie-statement",
        CookieStatementView.as_view(),
        name="cookie-statement",
    ),
    path(
        "support/terms-of-service",
        TermsOfServiceView.as_view(),
        name="terms-of-service",
    ),
    path("support/contact", ContactView.as_view(), name="contact"),
]
