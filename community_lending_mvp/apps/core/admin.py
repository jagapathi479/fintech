from django.contrib import admin
from .models import LoanRequest, Document, RepaymentInstallment, Payment
@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ('id','user','principal','status','created_at')
    actions = ['approve_loans']
    def approve_loans(self, request, queryset):
        from django.utils import timezone
        from .models import RepaymentInstallment
        for loan in queryset:
            loan.status = LoanRequest.APPROVED
            loan.approved_by = request.user
            loan.approved_at = timezone.now()
            loan.save()
            from dateutil.relativedelta import relativedelta
            from datetime import date
            monthly = loan.monthly_installment()
            start = date.today()
            for i in range(1, loan.tenure_months+1):
                due = start + relativedelta(months=i)
                RepaymentInstallment.objects.create(loan=loan, due_date=due, amount_due=monthly)
    approve_loans.short_description = 'Approve selected loans and generate installments'
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('loan','doc_type','uploaded_at')
@admin.register(RepaymentInstallment)
class RepaymentInstallmentAdmin(admin.ModelAdmin):
    list_display = ('loan','due_date','amount_due','is_paid')
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('loan','amount','method','created_at')
