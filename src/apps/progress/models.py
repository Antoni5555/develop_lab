"""Прогресс вошедшего пользователя. Строка есть — задача решена / урок открыт.

Прогресс гостя хранится в localStorage браузера (static/js/progress.js)
и переносится сюда после входа (api.ImportView).
"""
from django.conf import settings
from django.db import models

from apps.courses.models import Exercise, Lesson


class ExerciseProgress(models.Model):
    """Задача решена: «Проверить» вернула «Верно!»."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='solved_exercises',
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='+')
    solved_at = models.DateTimeField('решена', auto_now_add=True)

    class Meta:
        verbose_name = 'решённая задача'
        verbose_name_plural = 'решённые задачи'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'exercise'], name='progress_unique_solved',
            ),
        ]

    def __str__(self):
        return f'{self.user} — {self.exercise}'


class LessonView(models.Model):
    """Урок открыт (прочитан)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='viewed_lessons',
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='+')
    viewed_at = models.DateTimeField('открыт', auto_now_add=True)

    class Meta:
        verbose_name = 'прочитанный урок'
        verbose_name_plural = 'прочитанные уроки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'lesson'], name='progress_unique_viewed',
            ),
        ]

    def __str__(self):
        return f'{self.user} — {self.lesson}'
