from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls', namespace='home')),
    path('source/', include('source.urls', namespace='source')),
    path('registration/', include('registration.urls',
                                  namespace='registration')),
    path('support/', include('support.urls', namespace='support')),
]
