# Сборка в два этапа: в итоговый образ попадает только готовое окружение,
# без pip-кэша и инструментов сборки.

# --- 1. Ставим зависимости в отдельное виртуальное окружение ---
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

COPY requirements.txt .
RUN pip install -r requirements.txt


# --- 2. Итоговый образ ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/venv/bin:$PATH

# Приложение работает не от root: если его взломают, у процесса минимум прав
RUN useradd --create-home --uid 1000 app

COPY --from=builder /venv /venv

WORKDIR /app
COPY --chown=app:app src/ .

# Контент для load_content (на сервере — отдельный шаг деплоя после миграций)
COPY --chown=app:app content/ /content/
ENV CONTENT_DIR=/content

# Статика собирается при сборке образа: у каждой версии образа своя статика.
# SECRET_KEY здесь фиктивный — collectstatic ничего не шифрует и не ходит в БД.
RUN DJANGO_SETTINGS_MODULE=config.settings.production SECRET_KEY=collectstatic \
    python manage.py collectstatic --noinput

USER app

EXPOSE 8000

# Миграции здесь не запускаются — это отдельный шаг деплоя
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--threads", "4", "--worker-class", "gthread"]
