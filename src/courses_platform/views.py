from django.shortcuts import render
from emails.models import Email, EmailVerification

from emails.forms import EmailForm
from emails import services as email_services

from django.utils import timezone
from django.http import JsonResponse

def home(request, *args, **kwargs):
    template_name = "home.html"
    print(request.POST)
    form = EmailForm(request.POST or None)
    context = {
        "form": form,
        "message": "", 
    }
    if form.is_valid():
        email_val = form.cleaned_data.get("email")
        obj = email_services.start_verification_event(email=email_val)
        #obj = form.save()
        email_obj, created = Email.objects.get_or_create(email=email_val)
        EmailVerification.objects.create(
            parent=email_obj,
            email=email_val,

        )
        context["form"] = EmailForm()
        context["message"] = f"Success!, Check your email for verification for {1+1}"
    print('email_id', request.session.get('email_id'))
    return render(request, template_name, context)

