from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from .forms import RegistrationForm, OTPVerifyForm
from .models import PhoneOTP, User
from datetime import timedelta
import random
def send_sms(to, message):
    try:
        from twilio.rest import Client as TwilioClient
    except Exception:
        TwilioClient = None
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER and TwilioClient:
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=to)
            return True
        except Exception as e:
            print('Twilio send error:', e)
    print(f"SMS to {to}: {message}")
    return True
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            code = f"{random.randint(100000, 999999):06d}"
            otp = PhoneOTP.objects.create(user=user, code=code, valid_until=timezone.now() + timedelta(minutes=10))
            send_sms(user.phone_number or '', f"Your verification code: {code}")
            request.session['pending_user_id'] = user.id
            return redirect('users:verify_phone')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})
def verify_phone_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, 'No pending registration found.')
        return redirect('users:register')
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otps = PhoneOTP.objects.filter(user=user, code=code).order_by('-created_at')
            if otps and otps[0].is_valid():
                user.phone_verified = True
                user.email_verified = True
                user.save()
                login(request, user)
                messages.success(request, 'Phone verified and logged in')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Invalid or expired code')
    else:
        form = OTPVerifyForm()
    return render(request, 'users/verify_phone.html', {'form': form, 'user': user})
