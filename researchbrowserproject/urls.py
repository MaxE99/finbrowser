# Django imports
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

# Local imports
from researchbrowserproject.sitemaps import (
    SectorSitemap,
    RegistrationSitemaps,
    SourceSitemap,
    ContentSitemaps,
)

from apps.home.views import NotFoundView

sitemaps = {
    "sources": SourceSitemap,
    "sectors": SectorSitemap,
    "content": ContentSitemaps,
    "registration": RegistrationSitemaps,
}


urlpatterns = [
    path("", include("apps.home.urls", namespace="home")),
    path("", include("apps.source.urls", namespace="source")),
    path("", include("apps.support.urls", namespace="support")),
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("", include("apps.list.urls", namespace="list")),
    path("", include("apps.sector.urls", namespace="sector")),
    path("", include("apps.stock.urls", namespace="stock")),
    path("registration/", include("allauth.urls")),
    path("api/", include("apps.api.urls", namespace="api")),
    path("featodzbqawibezdahapryyiwedjydbeadefsdxnwvtlw/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = NotFoundView.as_view()
