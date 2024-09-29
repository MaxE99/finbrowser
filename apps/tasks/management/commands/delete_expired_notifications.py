from typing import Any
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand

from apps.home.models import NotificationMessage


class Command(BaseCommand):
    """
    Django management command to delete expired notification messages.

    This command removes all notification messages that are older than 24 hours.
    """

    help = "Removes notification messages that are more than 24 hours old."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to delete expired notification messages.

        Notification messages older than 24 hours are removed from the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        NotificationMessage.objects.filter(
            date__lte=timezone.now() - timedelta(hours=24)
        ).delete()
        self.stdout.write(
            self.style.SUCCESS("Successfully deleted expired notifications.")
        )
