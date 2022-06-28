# Django Imports
from django.contrib import admin
# Local imports
from apps.home.models import Notification, NotificationMessage

admin.site.register(Notification)
admin.site.register(NotificationMessage)