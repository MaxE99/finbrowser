from django.core.management.base import BaseCommand


# Local imports
from apps.source.models import Source


class Command(BaseCommand):
    help = "Calculates similiar sources"

    def handle(self, *args, **kwargs):
        Source.objects.calc_similiar_sources()
        self.stdout.write("Finished calculating similiar sources!")
