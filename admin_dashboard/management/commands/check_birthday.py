from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from django.db.models import Sum
from admin_dashboard.models import Pelanggan, Notifikasi, Transaksi
from django.urls import reverse

class Command(BaseCommand):
    help = 'Check for customers with birthdays today and total spending >= 5 million'

    def handle(self, *args, **options):
        # Use the Celery task instead of direct implementation
        from admin_dashboard.tasks import check_birthday_and_loyalty_task
        result = check_birthday_and_loyalty_task.delay()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully triggered birthday and loyalty check task: {result.id}'
            )
        )
