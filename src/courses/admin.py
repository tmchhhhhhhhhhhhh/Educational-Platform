from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson


class LessonInline(admin.StackedInline): 
    model = Lesson
    extra = 1  
    fields = ['title', 'description', 'notebook_link', 'test_link', 'order', 'can_preview', 'status']
    show_change_link = True  


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'access', 'is_published', 'display_image']
    list_filter = ['status', 'access', 'author']
    fields = ['title', 'description', 'image', 'image_preview', 'access', 'status', 'author']
    readonly_fields = ['image_preview']
    inlines = [LessonInline]

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "—"
    display_image.short_description = "Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="object-fit:contain;border:1px solid #ccc;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = "Preview"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'status', 'can_preview']
    list_filter = ['status', 'can_preview']
    search_fields = ['title', 'description']
    ordering = ['course', 'order']
