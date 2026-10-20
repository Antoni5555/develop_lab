"""Админка контента — только для просмотра: контент меняется через content/
и команду load_content, иначе правка в админке пропала бы при следующей загрузке."""
from django.contrib import admin

from .models import Course, Exercise, Lesson, Section, Topic, Track


class ReadOnlyAdmin(admin.ModelAdmin):
    """Разрешает только смотреть."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Track)
class TrackAdmin(ReadOnlyAdmin):
    list_display = ['title', 'slug', 'order', 'is_published']


@admin.register(Course)
class CourseAdmin(ReadOnlyAdmin):
    list_display = ['title', 'slug', 'track', 'engine', 'order', 'is_published']
    list_filter = ['track', 'engine', 'is_published']


@admin.register(Section)
class SectionAdmin(ReadOnlyAdmin):
    list_display = ['title', 'course', 'level', 'order', 'is_published']
    list_filter = ['course', 'is_published']


@admin.register(Topic)
class TopicAdmin(ReadOnlyAdmin):
    list_display = ['title', 'section', 'order', 'is_published']
    list_filter = ['section__course', 'is_published']


@admin.register(Lesson)
class LessonAdmin(ReadOnlyAdmin):
    list_display = ['title', 'topic', 'reading_time', 'is_published']


@admin.register(Exercise)
class ExerciseAdmin(ReadOnlyAdmin):
    list_display = ['title', 'topic', 'type', 'difficulty', 'order', 'is_published']
    list_filter = ['type', 'topic__section__course', 'is_published']
