# Django imports
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
# Local imports
from accounts.sitemaps import ProfileSitemap
from home.sitemaps import (SourceSitemap, ListSitemap, SectorSitemap,
                           ContentSitemaps, HomePageSitemap)
from support.sitemaps import SupportSitemaps
from registration.sitemaps import RegistrationSitemaps

sitemaps = {
    'sources': SourceSitemap,
    'lists': ListSitemap,
    'sectors': SectorSitemap,
    'profile': ProfileSitemap,
    'content': ContentSitemaps,
    'home': HomePageSitemap,
    'registration': RegistrationSitemaps,
    'support': SupportSitemaps
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls', namespace='home')),
    path('source/', include('source.urls', namespace='source')),
    path('support/', include('support.urls', namespace='support')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('sitemap.xml',
         sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('registration/', include('allauth.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
