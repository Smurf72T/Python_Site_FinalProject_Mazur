# Docker инструкция для проекта Rental

## Структура контейнеров

| Контейнер | Порт | Описание |
|-----------|------|----------|
| `rental_db` | 5432 | PostgreSQL база данных |
| `rental_backend` | 8000 | Основное приложение |
| `rental_admin` | 8001 | Django админка (отдельно) |
| `rental_tests` | - | Автоматические тесты |

## Быстрый старт

### 1. Запуск всех контейнеров

```bash
docker-compose up --build
```

### 2. Проверка статуса

```bash
docker-compose ps
```

### 3. Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Лог конкретного контейнера
docker-compose logs -f backend
docker-compose logs -f admin
docker-compose logs -f tests
```

## Доступ к сервисам

### Основное приложение
- URL: http://localhost:8000
- Описание: Основной сайт аренды одежды

### Django Admin
- URL: http://localhost:8001/admin/
- Login: `admin`
- Password: `admin123`
- Email: `admin@admin.admin`

### База данных
- Host: localhost
- Port: 5432
- Database: rental_db
- User: postgres
- Password: postgres

### Результаты тестов

После запуска тестов результаты доступны в папке:
- `./test_results/report.html` - HTML отчёт о тестах
- `./test_results/htmlcov/index.html` - Покрытие кода

## Отдельные команды

### Запуск только базы данных
```bash
docker-compose up -d db
```

### Запуск backend + db
```bash
docker-compose up -d backend db
```

### Запуск тестов вручную
```bash
docker-compose run --rm tests
```

### Перезапуск тестов
```bash
docker-compose run tests
```

### Остановка всех контейнеров
```bash
docker-compose down
```

### Остановка с удалением volumes
```bash
docker-compose down -v
```

## Автоматическая инициализация

При первом запуске автоматически:
1. ✅ Создаётся база данных
2. ✅ Применяются миграции
3. ✅ Создаётся superuser (admin/admin123)
4. ✅ Заполняются категории (15 шт.)
5. ✅ Заполняются города (10 шт.)
6. ✅ Запускаются тесты

## Отладка

### Вход в контейнер
```bash
# Backend
docker-compose exec backend bash

# Database
docker-compose exec db psql -U postgres -d rental_db

# Admin
docker-compose exec admin bash
```

### Выполнение команд
```bash
# Миграции
docker-compose exec backend python manage.py migrate

# Создание superuser
docker-compose exec backend python manage.py createsuperuser

# Заполнение данными
docker-compose exec backend python manage.py fill_categories
docker-compose exec backend python manage.py fill_cities

# Тесты
docker-compose exec backend python -m pytest apps/ -v
```

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `DJANGO_SETTINGS_MODULE` | config.settings | Настройки Django |
| `POSTGRES_DB` | rental_db | Имя базы данных |
| `POSTGRES_USER` | postgres | Пользователь БД |
| `POSTGRES_PASSWORD` | postgres | Пароль БД |

## Примечания

- Данные базы данных сохраняются в volume `postgres_data`
- Для полного сброса: `docker-compose down -v`
- Медиа-файлы монтируются из локальной папки `./media`
- Статика монтируется из локальной папки `./staticfiles`
