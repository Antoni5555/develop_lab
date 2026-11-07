from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from .models import Note


@admin.register(Note)
class NoteAdmin(ModelAdmin):
    """Заметки пишут пользователи на сайте: здесь только смотреть и удалять."""

    list_display = ['title', 'user', 'course', 'topic', 'updated_at']
    list_select_related = ['user', 'course', 'topic']
    list_filter = ['course']
    search_fields = ['title', 'user__email']
    readonly_fields = ['user', 'course', 'topic', 'exercise', 'title', 'body',
                       'created_at', 'updated_at']
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='текст')
    def body(self, obj):
        # body_html очищен nh3 при сохранении — показываем как на сайте
        return mark_safe(obj.body_html)
