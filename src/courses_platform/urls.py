from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path

from courses import views as courses_views
from . import views
from emails.views import (
    verify_email_token_view,
    email_token_login_view,
    logout_btn_hx_view,
    extend_session_view,
)

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("hx/login/", email_token_login_view),
    path("hx/logout/", logout_btn_hx_view, name="logout-hx"),
    path('hx/extend-session/', extend_session_view, name='extend-session'),
    path("verify/<uuid:token>/", verify_email_token_view),
    path("courses/", courses_views.course_list_view, name="course-list"),
    path(
        "courses/<int:course_id>/",
        courses_views.course_detail_view,
        name="course-detail",
    ),
    path(
        "courses/<int:course_id>/lessons/<int:lesson_id>/",
        courses_views.lesson_detail_view,
        name="lesson-detail",
    ),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
