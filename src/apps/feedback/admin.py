"""Админка сообщений об ошибках: что не так, где, и какой файл content/ править."""
from django.contrib import admin
from django.utils.html import format_html

from .models import ContentReport
from .services.reports import content_path


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = [
        'short_quote', 'short_comment', 'place', 'user', 'status', 'created_at',
    ]
    list_select_related = ['user', 'topic__section__course', 'exercise']
    list_filter = [
        'status', ('topic__section__course', admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = ['quote', 'comment']
    actions = ['mark_fixed', 'mark_rejected']
    readonly_fields = [
        'quote', 'context', 'comment', 'place', 'file', 'user', 'created_at',
    ]
    fields = ['status', *readonly_fields]

    def has_add_permission(self, request):
        return False   # сообщения пишут пользователи на сайте

    def get_queryset(self, request):
        # «Где» и путь к файлу на странице сообщения — без лишних запросов
        return super().get_queryset(request).select_related(
            'user', 'topic__section__course__track', 'exercise',
        )

    @admin.display(description='что выделено')
    def short_quote(self, obj):
        return obj.quote[:80] + ('…' if len(obj.quote) > 80 else '')

    @admin.display(description='комментарий')
    def short_comment(self, obj):
        return obj.comment[:80] + ('…' if len(obj.comment) > 80 else '')

    @admin.display(description='где')
    def place(self, obj):
        title = f'{obj.topic.section.course.title} › {obj.topic.title}'
        if obj.exercise:
            title += f' › {obj.exercise.title}'
        return format_html(
            '<a href="{}" target="_blank">{}</a>', obj.get_absolute_url(), title,
        )

    @admin.display(description='файл для правки')
    def file(self, obj):
        return format_html('<code>{}</code>', content_path(obj))

    @admin.action(description='Отметить: исправлено')
    def mark_fixed(self, request, queryset):
        queryset.update(status=ContentReport.Status.FIXED)

    @admin.action(description='Отметить: отклонено')
    def mark_rejected(self, request, queryset):
        queryset.update(status=ContentReport.Status.REJECTED)
