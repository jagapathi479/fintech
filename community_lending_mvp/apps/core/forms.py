from django import forms
from .models import LoanRequest, Document
class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ('principal','annual_interest_rate','tenure_months','purpose')
    def clean_principal(self):
        p = self.cleaned_data['principal']
        if p <= 0:
            raise forms.ValidationError('Principal must be greater than zero')
        if p > 1000000:
            raise forms.ValidationError('Principal exceeds allowed limit (hackathon cap)')
        return p
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('doc_type','file')
    def clean_file(self):
        f = self.cleaned_data['file']
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 5MB)')
        allowed = ['application/pdf','image/jpeg','image/png']
        if f.content_type not in allowed:
            raise forms.ValidationError('Unsupported file type')
        return f
class PaymentRecordForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    installment_id = forms.IntegerField()
