
UDP Mongo Logs Service
=====================

UDP Mongo Logs Service — это универсальный сервис для хранения и обработки данных логов и метрик производительности. 
Он включает интеграцию с MongoDB для хранения данных, UDP listener для обработки сообщений, и может быть дополнительно 
подключен к Metabase для визуализации логов и метрик.

Описание сервиса
----------------
- UDP listener: Обрабатывает сообщения через протокол udp и записывает их в MongoDB.
- MongoDB: Неструктурированное хранилище данных для логов и метрик.
- Metabase: Используется для визуализации данных, таких как логи и метрики производительности (опционально, может быть заменено вашим собственным фронтендом).

Запуск с помощью Docker Compose
-------------------------------
Пример `docker-compose.yml` приведен ниже:

```
version: "3.8"

services:
  rabbit-logger:
    build: .
    ports:
      - "8123:8123"     # ClickHouse HTTP-interface
      - "9000:9000"     # ClickHouse TCP-interface
      - "5672:5672"     # RabbitMQ AMQP
      - "9999:9999/udp" # UDP
    environment:
      - CLICKHOUSE_USER=clickhouse-user
      - CLICKHOUSE_PASSWORD=secret-password
      - LOG_RETENTION_DAYS=30
      - APM_RETENTION_DAYS=30
    volumes:
      - clickhouse_data:/var/lib/clickhouse

volumes:
  clickhouse_data:
```

Переменные окружения
---------------------
### Rabbit-logger
- CLICKHOUSE_USER: Имя пользователя для ClickHouse.
- CLICKHOUSE_PASSWORD: Пароль для пользователя ClickHouse.
- LOG_RETENTION_DAYS: Число дней для хранения логов (по умолчанию 30).
- APM_RETENTION_DAYS: Число дней для хранения метрик (по умолчанию 30).

Также вы можете добавить визуальное отображение для ваших логов и apm, добавив в docker-compose.yml:
---------------------
```
  db:
    image: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=postgres
      - POSTGRES_USER=debug
      - POSTGRES_PASSWORD=debug
    ports:
      - "5434:5432"

  metabase:
    image: metabase/metabase:latest
    restart: always
    environment:
      - MB_DB_TYPE=postgres
      - MB_DB_DBNAME=postgres
      - MB_DB_PORT=5432
      - MB_DB_USER=debug
      - MB_DB_PASS=debug
      - MB_DB_HOST=db
    volumes:
      - ./clickhouse.metabase-driver.jar:/plugins/clickhouse.metabase-driver.jar
    ports:
      - 3000:3000
    depends_on:
      - db

volumes:
  postgres_data:
```
---------------------

### PostgreSQL (для Metabase)
- POSTGRES_HOST: Хост базы данных PostgreSQL.
- POSTGRES_PORT: Порт PostgreSQL (по умолчанию 5432).
- POSTGRES_DB: Имя базы данных.
- POSTGRES_USER: Имя пользователя базы данных.
- POSTGRES_PASSWORD: Пароль для PostgreSQL.

### Metabase
- MB_DB_TYPE: Тип базы данных для хранения конфигурации Metabase (PostgreSQL).
- MB_DB_DBNAME: Имя базы данных для Metabase.
- MB_DB_PORT: Порт базы данных Metabase.
- MB_DB_USER: Имя пользователя для Metabase.
- MB_DB_PASS: Пароль для Metabase.
- MB_DB_HOST: Хост базы данных Metabase.

Использование
-------------
1. Запуск Rabbit Logger:
   ```bash
   docker-compose up -d
   ```

2. Подключение Metabase:
   - Перейдите в Metabase через `http://localhost:3000`.
   - Подключите базу ClickHouse (укажите HTTP-порт ClickHouse: `8123`, host: `rabbit-logger`, логин и пароль, который вы указали в ClickHouse environment).

3. Визуализация логов:
   Используйте Metabase для построения графиков и визуализации данных из ClickHouse. Вы также можете разработать свой фронтенд, если Metabase не подходит.

4. Очистка данных:
   Логи и метрики старше указанного периода (например, `LOG_RETENTION_DAYS=30`) автоматически удаляются с помощью запущенного в контейнере cron-задания.

Настройка своего фронтенда
--------------------------
Если вы предпочитаете использовать собственное приложение вместо Metabase:
- Подключитесь к ClickHouse через его HTTP- или TCP-интерфейсы.
- Используйте API ClickHouse для выполнения SQL-запросов и извлечения данных.

Пример SQL-запроса для получения последних 100 записей из логов:
```sql
SELECT * 
FROM rabbit_logger.logs
ORDER BY created_dt DESC
LIMIT 100;
```

Полезные команды
-----------------
- Проверить состояние контейнеров:
  ```bash
  docker-compose ps
  ```

- Проверить логи:
  ```bash
  docker logs <container_name>
  ```

Сервис готов к использованию! 🎉