# Django imports
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView

# Local imports
from researchbrowserproject.sitemaps import (
    SectorSitemap,
    RegistrationSitemaps,
    SourceSitemap,
    ContentSitemaps,
    StockSitemap,
)

from apps.home.views import NotFoundView, error_view

sitemaps = {
    "sources": SourceSitemap,
    "sectors": SectorSitemap,
    "content": ContentSitemaps,
    "stocks": StockSitemap,
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
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="home/robots.txt", content_type="text/plain"
        ),
    ),
    # path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = NotFoundView.as_view()
handler500 = error_view
