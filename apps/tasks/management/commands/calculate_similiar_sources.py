from typing import Any

from django.core.management.base import BaseCommand

from apps.source.models import Source


class Command(BaseCommand):
    """
    Django management command to calculate similar sources.

    This command utilizes the Source model to compute and
    update similar sources based on predefined logic or criteria.
    """

    help = "Analyzes and calculates similar sources for better recommendations."

    def handle(self, *args: Any, **kwargs: Any):
        """
        Executes the command to calculate similar sources.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        Source.objects.calc_similiar_sources()
        self.stdout.write(
            self.style.SUCCESS("Successfully calculated and updated similar sources.")
        )
