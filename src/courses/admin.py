from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Notebook


class LessonInline(admin.StackedInline): 
    model = Lesson
    extra = 1  
    fields = ['title', 'description', 'notebook_link', 'test_link', 'order', 'can_preview', 'status']
    show_change_link = True  


class NotebookInline(admin.TabularInline):
    model = Notebook
    extra = 0
    fields = ['title', 'file', 'github_repo', 'github_branch', 'order']
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
    list_display = ['title', 'course', 'order', 'status', 'can_preview', 'notebook_count']
    list_filter = ['status', 'can_preview']
    search_fields = ['title', 'description']
    ordering = ['course', 'order']
    inlines = [NotebookInline]
    
    def notebook_count(self, obj):
        count = obj.notebooks.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">📓 {}</span>',
                count
            )
        return format_html('<span style="color: gray;">—</span>')
    notebook_count.short_description = "Notebooks"


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'order', 'has_github', 'file_preview', 'created_at']
    list_filter = ['lesson__course', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['lesson', 'order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('lesson', 'title', 'description', 'file', 'order')
        }),
        ('Интеграция с GitHub (для Binder/Colab)', {
            'fields': ('github_repo', 'github_branch'),
            'description': 'Укажите GitHub репозиторий для запуска через Binder или Google Colab'
        }),
    )
    
    def has_github(self, obj):
        if obj.github_repo:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.github_repo
            )
        return format_html('<span style="color: red;">✗</span>')
    has_github.short_description = "GitHub"
    
    def file_preview(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">📄 {}</a>',
                obj.file.url,
                obj.file.name.split('/')[-1]
            )
        return "—"
    file_preview.short_description = "Файл"