from django.contrib import admin

from .models import ExerciseProgress, LessonView


@admin.register(ExerciseProgress)
class ExerciseProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'solved_at']
    list_select_related = ['user', 'exercise']
    raw_id_fields = ['user', 'exercise']


@admin.register(LessonView)
class LessonViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'viewed_at']
    list_select_related = ['user', 'lesson']
    raw_id_fields = ['user', 'lesson']
