from django.core.management.base import BaseCommand
from apps.core.models import RepaymentInstallment
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help = 'Send reminders for upcoming installments (console output)'
    def handle(self, *args, **options):
        today = timezone.now().date()
        upcoming = RepaymentInstallment.objects.filter(is_paid=False, due_date__gte=today, due_date__lte=today+timedelta(days=3))
        for inst in upcoming:
            user = inst.loan.user
            print(f"Reminder to {user.username} ({user.phone_number}): installment due on {inst.due_date} amount {inst.amount_due}")
