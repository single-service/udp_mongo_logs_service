FROM python:3.9-slim

# Установка общих зависимостей
RUN apt-get update && apt-get install -y \
    supervisor \
    nginx \
    default-jre-headless \
    curl wget \
    cron \
    && apt-get clean

# ==========================
# Конфигурация Listener
# ==========================
WORKDIR /app
COPY listener/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY listener/clean_logs.py /app/
COPY listener/listener.py /app/

# ==========================
# Настройка Cron
# ==========================
# Копируем cron задание
COPY cronjobs /etc/cron.d/clean_logs
# Устанавливаем права на cron задание
RUN chmod 0644 /etc/cron.d/clean_logs
# Применяем cron задание
RUN crontab /etc/cron.d/clean_logs
# Создаем файл логов для cron
RUN touch /var/log/cron.log

# ==========================
# Настройка Supervisor
# ==========================
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Создание директории для инициализационных файлов
RUN mkdir -p /docker-entrypoint-initdb.d

# Указываем Supervisor как команду запуска
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
