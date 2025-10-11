from django.contrib import admin

# Register your models here.

from .models import Email, EmailVerification

admin.site.register(Email)
admin.site.register(EmailVerification)