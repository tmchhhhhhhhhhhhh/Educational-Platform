from django.shortcuts import render
from django.urls import reverse
from emails.models import Email, EmailVerification
from emails.forms import EmailForm
from emails import services as email_services
from django.http import JsonResponse
from courses.models import Course, Notebook


def home(request, *args, **kwargs):
    template_name = "home.html"

    # --- EMAIL ЛОГИКА ---
    form = EmailForm(request.POST or None)
    context = {
        "form": form,
        "message": "",
    }

    if form.is_valid():
        email_val = form.cleaned_data["email"]
        email_services.start_verification_event(email=email_val)

        email_obj, _ = Email.objects.get_or_create(email=email_val)
        EmailVerification.objects.create(
            parent=email_obj,
            email=email_val,
        )

        context["form"] = EmailForm()
        context["message"] = f"Отлично! Проверьте доступ на вашей почте {email_val}"

    # --- ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ ДЛЯ HOME ---
    courses = Course.objects.all()

    # Безопасно получаем ноутбуки
    notebooks_raw = Notebook.objects.select_related(
        "lesson", "lesson__course"
    ).order_by("-created_at")

    safe_notebooks = []
    for nb in notebooks_raw:
        lesson_url = None

        # Проверка связей перед reverse()
        if (
            nb.lesson
            and nb.lesson_id
            and nb.lesson.course
            and nb.lesson.course_id
        ):
            try:
                lesson_url = reverse(
                    "lesson-detail",
                    args=[nb.lesson.course_id, nb.lesson_id]
                )
            except:
                lesson_url = None

        safe_notebooks.append({
            "nb": nb,
            "lesson_url": lesson_url,
            "lesson": nb.lesson,
            "course": nb.lesson.course if nb.lesson else None,
        })

    context["courses"] = courses
    context["notebooks"] = safe_notebooks

    return render(request, template_name, context)
