from django.contrib import admin

from apps.home.models import Notification, NotificationMessage

admin.site.register(Notification)
admin.site.register(NotificationMessage)
