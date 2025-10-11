from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from . import services


# Create your views here.
def course_list_view(request):
    queryset = services.get_publish_courses()
    print(queryset)
    #return JsonResponse({'data': [x.id for x in queryset]})
    context = {
        "object_list": queryset
    }
    print([x.path for x in queryset])
    return render(request, "courses/list.html", context)


def course_detail_view(request, course_id=None, *args, **kwargs):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404

    # Получаем уроки с PUBLISHED и COMING_SOON
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
    context = {
        "object": lesson_obj
    }
    #return JsonResponse({'data': lesson_obj.id})
    return render(request, "courses/lesson.html", context)

