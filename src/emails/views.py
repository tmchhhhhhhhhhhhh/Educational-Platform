from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from . import services
from .forms import EmailForm
from .models import Email, EmailVerification
from django_htmx.http import HttpResponseClientRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extend_session_view(request):
    """
    Продлевает сессию для активного пользователя.
    """
    if request.session.get('email_id'):
        request.session.modified = True
        return JsonResponse({"status": "ok", "message": "Сессия продлена"})
    return JsonResponse({"status": "expired", "message": "Сессия уже истекла"})



# Create your views here.

def logout_btn_hx_view(request):
    if not request.htmx:
        return redirect('/')
    if request.method == "POST":
        try:
            del request.session["email_id"]
        except:
            pass
    email_id_in_session = request.session.get('email_id')
    if not email_id_in_session:
        return HttpResponseClientRedirect('/')
    return render(request, "emails/hx/logout-btn.html", {})



def verify_email_token_view(request, token, *args, **kwargs):
    did_verify, msg, email_obj = services.verify_token(token)
    if not did_verify:
        try:
            del request.session['email_id']
        except:
            pass
        messages.error(request, msg)
        return redirect("/")
    messages.success(request, msg)
    request.session['email_id']=f"{email_obj.id}"
    next_url = request.session.get('next_url') or '/'
    if not next_url.startswith('/'):
        next_url = "/"
    return redirect("/courses/")

def email_token_login_view(request):
    if not request.htmx:
        return redirect('/')

    email_id_in_session = request.session.get('email_id')
    template_name = "emails/hx/form.html"
    form = EmailForm(request.POST or None)
    context = {
        "form": form,
        "message": "", 
        "show_form": not email_id_in_session
    }

    if form.is_valid():
        email_val = form.cleaned_data.get("email")
        obj = services.start_verification_event(email=email_val)
        email_obj, created = Email.objects.get_or_create(email=email_val)
        EmailVerification.objects.create(parent=email_obj, email=email_val)
        context["form"] = EmailForm()
        context["message"] = f"Отлично! Проверьте доступ на вашей почте {email_val}"
        # вместо редиректа — просто возвращаем обновлённый блок
        return render(request, template_name, context)

    return render(request, template_name, context)