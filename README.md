# Telegram Scheduler (Single‑User)

End‑to‑end, Dockerized MVP сервиса отложенных публикаций в Telegram для одного пользователя и одного канала. Входит Backend (FastAPI), Frontend (React), Caddy (reverse proxy). Все настройки в `.env`.

## Установка Docker и Docker Compose (Ubuntu)

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
docker --version && docker compose version
```

## Развёртывание

```bash
git clone https://github.com/misterflare/telegram-scheduler.git
cd telegram-scheduler
cp .env.template .env
nano .env  # заполните JWT_SECRET, ADMIN_*, TELEGRAM_*
cd infra
docker compose up -d --build
docker compose logs -f
```

Доступ:
- Frontend: `http://<IP_сервера>` (через Caddy) или `http://<IP_сервера>:5173`
- API: `http://<IP_сервера>/api` (прокси Caddy) или `http://<IP_сервера>:8000`

## Переменные окружения (основные)

```env
APP_ENV=production
TZ=Europe/Amsterdam
JWT_SECRET=change_me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_or_-100xxxxxxxxxx
UPLOAD_DIR=/data/uploads
DATABASE_URL=sqlite:////data/db.sqlite3
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
PUBLIC_BASE_URL=http://localhost
```

## HTTPS через Caddy (авто‑сертификаты)

Чтобы включить HTTPS с автоматическим выпуском сертификатов (Let’s Encrypt/ZeroSSL):

1) Подготовьте домен
- Пропишите DNS‑запись A/AAAA на IP вашего VPS (например, `scheduler.example.com`).
- Убедитесь, что фаерволл пропускает порты `80` и `443`:
  ```bash
  sudo ufw allow 80,443/tcp
  ```

2) Обновите Caddyfile
- Откройте `infra/caddy/Caddyfile` и замените содержимое на доменный хост. Уберите `auto_https off`.

Пример (`scheduler.example.com`):
```
{
  # Опционально: почта для уведомлений ACME
  email you@example.com
}

scheduler.example.com {
  handle_path /api/* {
    uri strip_prefix /api
    reverse_proxy backend:8000
  }
  handle /* {
    reverse_proxy frontend:80
  }
}
```

3) Перезапустите Compose
```bash
cd infra
docker compose up -d --build
docker compose logs -f caddy  # следите за выдачей сертификатов
```

Подсказки:
- На время первичной выдачи сертификата домен должен указывать напрямую на сервер (без «оранжевого облака» Cloudflare). Если используете Cloudflare Proxy, временно выключите проксирование (сделайте «серую тучку») или настраивайте DNS‑челлендж через плагин caddy‑dns (в этот образ не включён).
- Обновите `PUBLIC_BASE_URL` в `.env` на `https://scheduler.example.com`.
- Если сертификат не выдался — проверьте DNS, открытые порты и системное время (`timedatectl`).

## Обновление

```bash
cd /path/to/telegram-scheduler
git pull
cd infra
docker compose up -d --build
```

## Частые проблемы

- Авторизация 401: истёк токен — войдите снова; проверьте `JWT_SECRET` (при смене секрета старые токены становятся недействительными).
- Публикация не идёт: добавьте бота админом в канал, проверьте `TELEGRAM_CHANNEL_ID` (`@username` или `-100…`).
- HTTPS не включается: домен не указывает на сервер, порты 80/443 закрыты фаерволом, Cloudflare Proxy включён (выключите на время выпуска сертификата), неверное системное время.
- Доступы: для продакшна закройте прямые порты 5173/8000 фаерволом и оставьте внешними только 80/443 (через Caddy).
- Время публикаций: UI сохраняет время в UTC, сервер использует `TZ` из `.env` — убедитесь, что значение `TZ` верное для вашего графика.
=======
# Telegram Scheduler (Single‑User)

End‑to‑end, Dockerized MVP сервиса отложенных публикаций в Telegram для одного пользователя и одного канала. Входит Backend (FastAPI), Frontend (React), Caddy (reverse proxy). Все настройки в `.env`.

## Установка Docker и Docker Compose (Ubuntu)

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
docker --version && docker compose version
```

## Развёртывание

```bash
git clone https://github.com/<yourname>/telegram-scheduler.git
cd telegram-scheduler
cp .env.template .env
nano .env  # заполните JWT_SECRET, ADMIN_*, TELEGRAM_*
cd infra
docker compose up -d --build
docker compose logs -f
```

Доступ:
- Frontend: `http://<IP_сервера>` (через Caddy) или `http://<IP_сервера>:5173`
- API: `http://<IP_сервера>/api` (прокси Caddy) или `http://<IP_сервера>:8000`

## Переменные окружения (основные)

```env
APP_ENV=production
TZ=Europe/Amsterdam
JWT_SECRET=change_me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_or_-100xxxxxxxxxx
UPLOAD_DIR=/data/uploads
DATABASE_URL=sqlite:////data/db.sqlite3
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
PUBLIC_BASE_URL=http://localhost
```

## HTTPS через Caddy (авто‑сертификаты)

Чтобы включить HTTPS с автоматическим выпуском сертификатов (Let’s Encrypt/ZeroSSL):

1) Подготовьте домен
- Пропишите DNS‑запись A/AAAA на IP вашего VPS (например, `scheduler.example.com`).
- Убедитесь, что фаерволл пропускает порты `80` и `443`:
  ```bash
  sudo ufw allow 80,443/tcp
  ```

2) Обновите Caddyfile
- Откройте `infra/caddy/Caddyfile` и замените содержимое на доменный хост. Уберите `auto_https off`.

Пример (`scheduler.example.com`):
```
{
  # Опционально: почта для уведомлений ACME
  email you@example.com
}

scheduler.example.com {
  handle_path /api/* {
    uri strip_prefix /api
    reverse_proxy backend:8000
  }
  handle /* {
    reverse_proxy frontend:80
  }
}
```

3) Перезапустите Compose
```bash
cd infra
docker compose up -d --build
docker compose logs -f caddy  # следите за выдачей сертификатов
```

Подсказки:
- На время первичной выдачи сертификата домен должен указывать напрямую на сервер (без «оранжевого облака» Cloudflare). Если используете Cloudflare Proxy, временно выключите проксирование (сделайте «серую тучку») или настраивайте DNS‑челлендж через плагин caddy‑dns (в этот образ не включён).
- Обновите `PUBLIC_BASE_URL` в `.env` на `https://scheduler.example.com`.
- Если сертификат не выдался — проверьте DNS, открытые порты и системное время (`timedatectl`).

## Обновление

```bash
cd /path/to/telegram-scheduler
git pull
cd infra
docker compose up -d --build
```

## Частые проблемы

- Авторизация 401: истёк токен — войдите снова; проверьте `JWT_SECRET` (при смене секрета старые токены становятся недействительными).
- Публикация не идёт: добавьте бота админом в канал, проверьте `TELEGRAM_CHANNEL_ID` (`@username` или `-100…`).
- HTTPS не включается: домен не указывает на сервер, порты 80/443 закрыты фаерволом, Cloudflare Proxy включён (выключите на время выпуска сертификата), неверное системное время.
- Доступы: для продакшна закройте прямые порты 5173/8000 фаерволом и оставьте внешними только 80/443 (через Caddy).
- Время публикаций: UI сохраняет время в UTC, сервер использует `TZ` из `.env` — убедитесь, что значение `TZ` верное для вашего графика.
>>>>>>> b5234bb (feat: scaffold Telegram Scheduler project, docs and infra)
