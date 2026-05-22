from django.core.management.base import BaseCommand
from apps.data_collection.collect import collect_day_ahead


class Command(BaseCommand):
    help = "Collecte le day-ahead RTE et stocke en base"

    def handle(self, *args, **options):
        self.stdout.write("Démarrage de la collecte...")
        collect_day_ahead()
        self.stdout.write(self.style.SUCCESS("Collecte terminée"))