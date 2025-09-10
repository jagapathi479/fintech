from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoanRequestForm
from .models import LoanRequest, Document, RepaymentInstallment, Payment
from dateutil.relativedelta import relativedelta
from datetime import date
@login_required
def dashboard(request):
    loans = request.user.loans.all().order_by('-created_at')
    upcoming = RepaymentInstallment.objects.filter(loan__user=request.user, is_paid=False).order_by('due_date')[:10]
    payments = Payment.objects.filter(loan__user=request.user).order_by('-created_at')[:10]
    return render(request, 'core/dashboard.html', {'loans': loans, 'upcoming': upcoming, 'payments': payments})
@login_required
def loan_request_view(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        files = request.FILES.getlist('docs')
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.status = LoanRequest.PENDING
            loan.save()
            for f in files:
                doc = Document(loan=loan, doc_type='KYC', file=f)
                doc.save()
            messages.success(request, 'Loan request submitted successfully')
            return redirect('core:dashboard')
    else:
        form = LoanRequestForm()
    return render(request, 'core/loan_request.html', {'form': form})
@login_required
def loan_detail_view(request, pk):
    loan = get_object_or_404(LoanRequest, pk=pk, user=request.user)
    installments = loan.installments.order_by('due_date')
    return render(request, 'core/loan_detail.html', {'loan': loan, 'installments': installments})
