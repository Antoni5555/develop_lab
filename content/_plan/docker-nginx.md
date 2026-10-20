# Курс: Docker и Nginx — карта

Источники:
- `training_skills/Docker/DOCKER_basic_command.md` — основы Docker + Postgres в контейнере (далее **DB**)
- `training_skills/Docker/clear_docker_imaage.md` — очистка Docker
- `DevOps/Nginx/nginx.md` — Nginx перед Django, `proxy_cache`
- `training_skills/nginx_gunicorn.md` — деплой Django: Gunicorn, Nginx, SSL, .env
- `training_skills/website_performance_optimization.md` — отчёт об оптимизации своего сайта
- `middle_course/new_admin_panel_sprint_2|3/docker_compose` — примеры docker-compose (код)

Легенда — в [00-overview.md](00-overview.md). ⚠️ Живого запуска в браузере нет: задачи — «собери/исправь Dockerfile/конфиг», проверка по правилам.

## Docker
| Тема | Покрытие | Комментарий |
|---|---|---|
| Что такое контейнер и образ, зачем Docker | 🟡 | DB «Что такое контейнер?» — коротко |
| Команды: `run`, `ps`, `stop`, `rm`, `exec`, `logs` | ✅ | DB «Основные команды», «Запуск» |
| Порты, переменные окружения | ✅ | DB (на примере Postgres) |
| Volumes и монтирование | ✅ | DB «Работа с файлами» |
| Dockerfile: `FROM`, `COPY`, `RUN`, `CMD`, слои и кэш | ❌ | главное, чего нет |
| docker-compose: сервисы, сети, `depends_on` | ❌ | есть только код в `middle_course` |
| Очистка: `prune`, логи | ✅ | `clear_docker_imaage.md` — «дополнительно» |

## Nginx и деплой
| Тема | Покрытие | Комментарий |
|---|---|---|
| Что такое веб-сервер, Nginx vs Gunicorn (WSGI) | 🟡 | `nginx.md` §1–2, `nginx_gunicorn.md` §6 |
| Конфиг: `server`, `location`, `proxy_pass` | 🟡 | `nginx_gunicorn.md` §7 |
| Раздача статики и медиа | 🟡 | `nginx_gunicorn.md` §10 |
| HTTPS, Let's Encrypt | 🟡 | `nginx_gunicorn.md` §8 — инструкция |
| Кэширование `proxy_cache` | ✅ | `nginx.md` §3–4, `website_performance_optimization.md` — подробно |
| Частые ошибки (502, 413, права) | ✅ | `nginx_gunicorn.md` §13 — хорошее сырьё для задач «найди ошибку» |

## Лишнее
- Деплой React (`nginx_gunicorn.md` §9), Git/venv/Django-команды там же — к курсу не относятся.
- `website_performance_optimization.md` — отчёт про конкретный сайт; брать идеи, не структуру.

## Итог
Есть практика «как сделать», мало «почему». Писать с нуля: Dockerfile, docker-compose, базовый конфиг Nginx как тема. Вероятно, курс стоит разделить на два — «Docker» и «Nginx» (в `docs/architecture.md` они упомянуты как отдельные будущие тренажёры).
