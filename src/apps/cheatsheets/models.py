"""Заметки пользователя.

Шпаргалка курса — не отдельная модель, а заметки пользователя по темам курса.
"""
from django.conf import settings
from django.db import models

from apps.courses.models import Course, Exercise, Topic


class Note(models.Model):
    """Заметка: заголовок (пишет сам пользователь) и текст с форматированием.

    Тема — где написана (урок или задача темы). Пустая тема — «Из тренажёра».
    body_html уже очищен (services/notes.py → nh3): в шаблоне выводится как есть.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes',
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='+')
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='+',
    )
    # задача, на странице которой написана заметка — для подписи «из задачи «…»»
    exercise = models.ForeignKey(
        Exercise, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    title = models.CharField('заголовок', max_length=200)
    body_html = models.TextField('текст (очищенный HTML)', blank=True)
    created_at = models.DateTimeField('создана', auto_now_add=True)
    updated_at = models.DateTimeField('изменена', auto_now=True)

    class Meta:
        verbose_name = 'заметка'
        verbose_name_plural = 'заметки'
        ordering = ['created_at']
        indexes = [models.Index(fields=['user', 'course'])]

    def __str__(self):
        return self.title
