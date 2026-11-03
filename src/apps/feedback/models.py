"""Сообщение об ошибке в контенте: пользователь выделил текст и написал, что не так.

Исправляют не в базе, а в файле content/ (load_content перезаписал бы правку),
поэтому сообщение — только задание автору: где ошибка и что в ней.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.courses.models import Exercise, Topic


class ContentReport(models.Model):

    class Status(models.TextChoices):
        NEW = 'new', 'новое'
        FIXED = 'fixed', 'исправлено'
        REJECTED = 'rejected', 'отклонено'

    # Пользователь удалил аккаунт — сообщение об ошибке всё ещё полезно
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='content_reports', verbose_name='пользователь',
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='reports', verbose_name='тема',
    )
    # Пусто — ошибка в уроке темы, иначе — в условии или разборе задачи
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, null=True, blank=True,
        related_name='reports', verbose_name='задача',
    )
    quote = models.TextField('выделенный текст')
    # Абзац, где выделили: одна и та же фраза может встречаться в уроке несколько раз
    context = models.TextField('текст вокруг', blank=True)
    comment = models.TextField('комментарий', blank=True)
    status = models.CharField(
        'статус', max_length=20, choices=Status.choices, default=Status.NEW,
    )
    created_at = models.DateTimeField('отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'сообщение об ошибке'
        verbose_name_plural = 'сообщения об ошибках'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', '-created_at'])]

    def __str__(self):
        return self.quote[:60]

    def get_absolute_url(self):
        """Страница, где нашли ошибку.

        Адрес собираем от self.topic, а не от exercise.topic: тема уже загружена
        через select_related, и список в админке не делает запрос на каждую строку.
        """
        if self.exercise is None:
            return self.topic.get_absolute_url()
        section = self.topic.section
        return reverse('trainers:exercise', args=[
            section.course.slug, section.slug, self.topic.slug, self.exercise.slug,
        ])
