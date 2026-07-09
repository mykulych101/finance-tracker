from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fetch the latest exchange rates from Monobank and persist them."

    def add_arguments(self, parser):
        parser.add_argument(
            "--async",
            action="store_true",
            dest="run_async",
            help="Dispatch the refresh to a Celery worker instead of running inline.",
        )

    def handle(self, *args, **options):
        from integrations.tasks import refresh_exchange_rates

        if options["run_async"]:
            refresh_exchange_rates.delay()
            self.stdout.write(self.style.SUCCESS("Exchange rate refresh dispatched to Celery."))
            return

        refresh_exchange_rates()
        self.stdout.write(self.style.SUCCESS("Exchange rates refreshed."))
