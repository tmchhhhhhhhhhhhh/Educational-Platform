

from .models import Course, PublishStatus, Lesson


def get_publish_courses():

    return Course.objects.filter(status=PublishStatus.PUBLISHED)

def get_course_detail(course_id=None):
    if course_id is None:
        return None
    obj = None
    try:
        obj = Course.objects.get(
            status=PublishStatus.PUBLISHED,
            id=course_id
        )
    except:
        pass
    return obj

def get_lesson_detail(course_id=None, lesson_id=None):
    if lesson_id is None or course_id is None:
        return None
    try:
        return Lesson.objects.get(
            course__id=course_id,
            course__status=PublishStatus.PUBLISHED,
            status__in=[PublishStatus.PUBLISHED, PublishStatus.COMING_SOON],
            id=lesson_id
        )
    except Lesson.DoesNotExist:
        return None




