from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'course', 'topic', 'updated_at']
    list_select_related = ['user', 'course', 'topic']
    list_filter = ['course']
    raw_id_fields = ['user', 'topic', 'exercise']
