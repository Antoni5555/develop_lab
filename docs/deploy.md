# Деплой

## Как устроено

```
git push в main
  → CI: flake8, pytest
  → CI: сборка образов web и nginx (тег = SHA коммита) → GitHub Container Registry
  → CI: по SSH на сервер: deploy.sh <sha>
        pull → migrate → load_content → up -d (ждём healthcheck)
```

| Файл | Что делает |
|---|---|
| `Dockerfile` | два образа: `web` (Django + Gunicorn) и `nginx` (Nginx + статика той же версии) |
| `deploy/nginx/default.conf.template` | Nginx: HTTPS, редирект с HTTP, статика с долгим кэшем, прокси в Django |
| `docker-compose.prod.yml` | сервисы на сервере: db, redis, web, nginx, certbot |
| `deploy/deploy.sh` | выкатить версию: `sh deploy.sh <sha>` (CI и ручной откат) |
| `.env.prod.example` | пример `.env` для сервера |
| `.github/workflows/ci.yml` | job `images` (сборка и отправка образов), job `deploy` |

Главные правила:
- **Деплой только после зелёных тестов**: job `deploy` зависит от `images`, а тот — от `lint` и `tests`.
- **Без `down`**: старые контейнеры работают, пока новые не прошли healthcheck.
- **Миграции и `load_content` — отдельными шагами** перед запуском новой версии. Если они упали, сайт остаётся на старой версии.
- Наружу открыт только Nginx (порты 80 и 443). База и Redis доступны только внутри Docker.

Пока сервера нет, job `deploy` пропускается: он включается переменной `DEPLOY_ENABLED`.

## Сервер: один раз

Нужен VPS с Ubuntu 24.04, 2 ГБ RAM (1 ГБ впритык), Docker Engine и домен, направленный на IP сервера (A-запись).

### 1. Пользователь для деплоя и Docker

Под root:

```bash
adduser --disabled-password deploy
usermod -aG docker deploy        # после установки Docker Engine
```

### 2. SSH-ключ для CI

На своём компьютере:

```bash
ssh-keygen -t ed25519 -f deploy_key -C "github-actions" -N ""
```

- Содержимое `deploy_key.pub` → на сервере в `/home/deploy/.ssh/authorized_keys`.
- Содержимое `deploy_key` (приватный) → секрет GitHub `SSH_PRIVATE_KEY` (см. ниже). Потом файл удалить.
- Отпечаток сервера для `SSH_KNOWN_HOSTS`: `ssh-keyscan <IP-сервера>`.

### 3. Папка и `.env`

Под пользователем `deploy`:

```bash
mkdir ~/develop_lab && cd ~/develop_lab
nano .env       # содержимое — из .env.prod.example, заполнить всё
```

`IMAGE_TAG` — SHA последнего коммита `main`, для которого CI собрал образы (видно во вкладке Actions).

Скопировать с компьютера `docker-compose.prod.yml` (как `docker-compose.yml`) и `deploy/deploy.sh`. При следующих деплоях это делает CI:

```bash
scp docker-compose.prod.yml deploy@<IP>:develop_lab/docker-compose.yml
scp deploy/deploy.sh deploy@<IP>:develop_lab/deploy.sh
```

### 4. Первый сертификат HTTPS

Nginx не стартует без сертификата, поэтому первый сертификат выпускаем сами, пока порт 80 свободен:

```bash
docker compose run --rm -p 80:80 --entrypoint certbot certbot \
  certonly --standalone -d <домен> -m <email> --agree-tos --no-eff-email
```

Дальше сертификат продлевает контейнер `certbot`, а Nginx раз в 12 часов его перечитывает.

### 5. Первый запуск

Образы в GHCR привязаны к публичному репозиторию, поэтому для скачивания вход не нужен. Если пакет окажется приватным, сначала выполнить `docker login ghcr.io` с личным токеном (`read:packages`).

```bash
sh deploy.sh <IMAGE_TAG>
docker compose exec web python manage.py createsuperuser
```

Проверка: `https://<домен>/health/` → `ok`.

### 6. Включить автодеплой в GitHub

Settings → Secrets and variables → Actions:

| Тип | Имя | Значение |
|---|---|---|
| Secret | `SSH_HOST` | IP сервера |
| Secret | `SSH_USER` | `deploy` |
| Secret | `SSH_PRIVATE_KEY` | приватный ключ из шага 2 |
| Secret | `SSH_KNOWN_HOSTS` | вывод `ssh-keyscan <IP>` |
| Variable | `DEPLOY_ENABLED` | `true` |

Job `deploy` использует environment `production`: в Settings → Environments можно, например, требовать ручное подтверждение каждого деплоя.

## Повседневное

Все команды — на сервере в `~/develop_lab`:

```bash
docker compose ps                         # что запущено, healthy ли web
docker compose logs -f web                # логи Django (и письма, пока нет SMTP)
docker compose logs -f nginx
sh deploy.sh <sha-прошлой-версии>         # откат (образы хранятся 7 дней)
```

Откат кода не откатывает миграции. Если новая миграция удалила или переименовала поле, просто откатиться нельзя. Поэтому такие изменения делаем в два релиза: сначала код перестаёт использовать поле, потом миграция.

## Ещё не сделано

- SMTP (провайдера выбираем вместе с хостингом). Пока `EMAIL_HOST` пуст, письма пишутся в лог `web`.
- Резервные копии базы (`pg_dump` по расписанию, копии — вне сервера).
- HSTS preload — когда будет постоянный домен (сейчас предупреждение `check --deploy` заглушено).
