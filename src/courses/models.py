from django.db import models
import helpers
from cloudinary.models import CloudinaryField
from django.urls import reverse

helpers.cloudinary_init()


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    COMING_SOON = "soon", "Coming Soon"
    PUBLISHED = "published", "Published"


class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    EMAIL_REQUIRED = "email", "Email Required"


def handle_upload(instance, filename):
    return f"{filename}"


def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, "title"):
        return instance.title
    elif hasattr(instance, "get_display_name"):
        return instance.get_display_name()
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField("image", blank=True, null=True)
    access = models.CharField(
        max_length=10,
        choices=AccessRequirement.choices,
        default=AccessRequirement.ANYONE,
    )
    status = models.CharField(
        max_length=10, choices=PublishStatus.choices, default=PublishStatus.DRAFT
    )
    author = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("course-detail", kwargs={"course_id": self.id})

    @property
    def path(self):
        return f"/courses/{self.id}"

    def get_display_name(self):
        return f"{self.title} - Course"

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED

    def __str__(self):
        return self.title

    def get_lessons(self, include_coming_soon=True):
        """
        Возвращает уроки курса.
        include_coming_soon=True → вернёт уроки со статусом PUBLISHED и COMING_SOON
        """
        lessons = self.lesson_set.all()
        if include_coming_soon:
            lessons = lessons.filter(
                status__in=[PublishStatus.PUBLISHED, PublishStatus.COMING_SOON]
            )
        else:
            lessons = lessons.filter(status=PublishStatus.PUBLISHED)
        return lessons.order_by("order")


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    notebook_link = models.URLField(blank=True, null=True)
    test_link = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(
        default=False, help_text="can user see this text?"
    )
    status = models.CharField(
        max_length=10, choices=PublishStatus.choices, default=PublishStatus.PUBLISHED
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def get_absolute_url(self):
        return reverse(
            "lesson-detail", kwargs={"course_id": self.course.id, "lesson_id": self.id}
        )

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED


class Notebook(models.Model):
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='notebooks',
        help_text="Урок, к которому привязан ноутбук"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="Название ноутбука"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Описание"
    )
    file = models.FileField(
        upload_to='notebooks/', 
        verbose_name="Jupyter Notebook файл (.ipynb)",
        help_text="Загрузите .ipynb файл"
    )
    github_repo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="GitHub репозиторий",
        help_text="Например: username/repo-name (для Binder)"
    )
    github_branch = models.CharField(
        max_length=100,
        default="main",
        verbose_name="Ветка GitHub",
        help_text="Обычно main или master"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="Порядок отображения"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Jupyter Notebook"
        verbose_name_plural = "Jupyter Notebooks"
    
    def __str__(self):
        return f"{self.title} ({self.lesson.title})"
    
    def get_binder_url(self):
        """Генерирует URL для Binder (интерактивный запуск)"""
        if self.github_repo:
            filepath = self.file.name.replace('notebooks/', '')
            return f"https://mybinder.org/v2/gh/{self.github_repo}/{self.github_branch}?filepath={filepath}"
        return None
    
    def get_absolute_url(self):
        return reverse("notebook-detail", kwargs={"notebook_id": self.id})