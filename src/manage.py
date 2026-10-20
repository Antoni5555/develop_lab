#!/usr/bin/env python
"""Утилита командной строки Django."""
import os
import sys


def main():
    """Запускает команду manage.py (по умолчанию — с настройками разработки)."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
