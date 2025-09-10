from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, PhoneOTP
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass
@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ('user','code','valid_until','created_at')
