from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Стандартная админка пользователей, но без username: вход по email."""

    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Имя', {'fields': ['first_name', 'last_name']}),
        ('Права', {'fields': ['is_active', 'is_staff', 'is_superuser',
                              'groups', 'user_permissions']}),
        ('Даты', {'fields': ['last_login', 'date_joined']}),
    ]
    add_fieldsets = [
        (None, {'classes': ['wide'], 'fields': ['email', 'password1', 'password2']}),
    ]
