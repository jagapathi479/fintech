from django.db import models
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
User = settings.AUTH_USER_MODEL
class LoanRequest(models.Model):
    PENDING='PENDING'; APPROVED='APPROVED'; REJECTED='REJECTED'; DISBURSED='DISBURSED'; CLOSED='CLOSED'
    STATUS_CHOICES=[(PENDING,'Pending'),(APPROVED,'Approved'),(REJECTED,'Rejected'),(DISBURSED,'Disbursed'),(CLOSED,'Closed')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.00)
    tenure_months = models.PositiveIntegerField()
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_loans')
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    def _quantize(self, value):
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    def total_interest(self):
        years = Decimal(self.tenure_months) / Decimal(12)
        p = Decimal(self.principal)
        r = Decimal(self.annual_interest_rate)
        interest = p * r * years / Decimal(100)
        return self._quantize(interest)
    def total_payable(self):
        return self._quantize(Decimal(self.principal) + self.total_interest())
    def monthly_installment(self):
        if self.tenure_months == 0:
            return Decimal('0.00')
        total = self.total_payable()
        monthly = total / Decimal(self.tenure_months)
        return self._quantize(monthly)
    def __str__(self):
        return f"Loan#{self.id} [{self.user}] {self.principal} - {self.status}"

class Document(models.Model):
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to='loan_docs/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class RepaymentInstallment(models.Model):
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='installments')
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    def mark_paid(self, amount, when=None):
        self.amount_paid += amount
        if self.amount_paid >= self.amount_due:
            self.is_paid = True
            self.paid_at = when or timezone.now()
        self.save()

class Payment(models.Model):
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='payments')
    installment = models.ForeignKey(RepaymentInstallment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, default='manual')
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
