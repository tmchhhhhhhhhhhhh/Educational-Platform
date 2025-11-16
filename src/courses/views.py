from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from . import services
from .models import Notebook
import nbformat
from nbconvert import HTMLExporter


def course_list_view(request):
    queryset = services.get_publish_courses()
    print(queryset)
    context = {
        "object_list": queryset
    }
    print([x.path for x in queryset])
    return render(request, "courses/list.html", context)


def course_detail_view(request, course_id=None, *args, **kwargs):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404

    lessons_queryset = course_obj.get_lessons(include_coming_soon=True)

    context = {
        "object": course_obj,
        "lessons_queryset": lessons_queryset
    }
    return render(request, "courses/detail.html", context)


def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    lesson_obj = services.get_lesson_detail(course_id=course_id, lesson_id=lesson_id)
    if lesson_obj is None:
        raise Http404
    email_id_exists = request.session.get('email_id')
    if lesson_obj.requires_email and not email_id_exists:
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    # Получаем все ноутбуки для этого урока (безопасно)
    try:
        notebooks = lesson_obj.notebooks.all().order_by('order')
    except:
        notebooks = []
    
    context = {
        "object": lesson_obj,
        "notebooks": notebooks
    }
    return render(request, "courses/lesson.html", context)


def notebook_detail_view(request, notebook_id=None, *args, **kwargs):
    """Отображение Jupyter Notebook со статическим превью"""
    notebook = get_object_or_404(Notebook, id=notebook_id)
    
    # Проверяем требования доступа
    email_id_exists = request.session.get('email_id')
    if notebook.lesson.requires_email and not email_id_exists:
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    # Конвертируем notebook в HTML для превью
    notebook_html = None
    error = None
    
    try:
        with notebook.file.open('r') as f:
            notebook_content = nbformat.read(f, as_version=4)
        
        html_exporter = HTMLExporter(template_name='classic')
        body, resources = html_exporter.from_notebook_node(notebook_content)
        notebook_html = body
    except Exception as e:
        error = str(e)
    
    context = {
        "notebook": notebook,
        "notebook_html": notebook_html,
        "error": error,
        "binder_url": notebook.get_binder_url(),
    }
    
    return render(request, "courses/notebook_detail.html", context)


def notebook_interactive_view(request, notebook_id=None, *args, **kwargs):
    """Страница для запуска интерактивного notebook через Binder"""
    notebook = get_object_or_404(Notebook, id=notebook_id)
    
    email_id_exists = request.session.get('email_id')
    if notebook.lesson.requires_email and not email_id_exists:
        request.session['next_url'] = request.path
        return render(request, "courses/email-required.html", {})
    
    context = {
        "notebook": notebook,
        "binder_url": notebook.get_binder_url(),
    }
    
    return render(request, "courses/notebook_interactive.html", context)