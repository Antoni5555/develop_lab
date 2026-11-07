from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ExerciseProgress, LessonView


class ProgressAdmin(ModelAdmin):
    """Прогресс отмечает сайт сам: здесь только смотреть (и удалять при сбросе)."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ExerciseProgress)
class ExerciseProgressAdmin(ProgressAdmin):
    list_display = ['user', 'exercise', 'solved_at']
    list_select_related = ['user', 'exercise']
    list_filter = ['solved_at']
    search_fields = ['user__email', 'exercise__title']


@admin.register(LessonView)
class LessonViewAdmin(ProgressAdmin):
    list_display = ['user', 'lesson', 'viewed_at']
    list_select_related = ['user', 'lesson']
    list_filter = ['viewed_at']
    search_fields = ['user__email', 'lesson__title']
