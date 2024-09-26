from django.core.management.base import BaseCommand

# Standard import
from datetime import timedelta

# Django import
from django.utils import timezone

# local imports
from apps.home.models import NotificationMessage


class Command(BaseCommand):
    help = "Deletes expired notifications"

    def handle(self, *args, **kwargs):
        NotificationMessage.objects.filter(
            date__lte=timezone.now() - timedelta(hours=24)
        ).delete()
        self.stdout.write("Deletes expired notifications!")
