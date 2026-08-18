# Docker окружение для проекта Rental

## Компоненты инфраструктуры

| Контейнер      | Порт  | Назначение                                        |
|----------------|-------|---------------------------------------------------|
| `rental_nginx` | 80    | Nginx reverse proxy (единая точка входа)          |
| `rental_db`    | 5432  | PostgreSQL сервер базы данных                     |
| `rental_backend`| -    | Основное приложение (доступно через nginx)        |
| `rental_admin` | -     | Django админка (доступно через nginx)             |
| `rental_tests` | -     | Автоматические тесты                              |

## Быстрый старт

### 1. Сборка всех контейнеров

```bash
docker-compose up --build
```

### 2. Проверить статус

```bash
docker-compose ps
```

## Ссылки и порты

### Основной сайт
- **URL:** http://localhost/
- **Назначение:** основной сайт, каталог объявлений

### Django Admin
- **URL:** http://localhost/admin/
- **Login:** `admin`
- **Password:** `admin123`
- **Email:** `admin@admin.admin`

### База данных
- Host: localhost
- Port: 5432
- Database: rental_db
- User: postgres
- Password: из переменной `POSTGRES_PASSWORD` (файл `.env` в корне проекта)

### Результаты тестов

После запуска тестов результаты сохраняются в папку:
- `./test_results/report.html` - HTML отчёт по тестам
- `./test_results/htmlcov/index.html` - покрытие кода

## Полезные команды

### Запустить только базу данных
```bash
docker-compose up -d db
```

### Запустить backend + db
```bash
docker-compose up -d backend db
```

### Запустить тесты повторно
```bash
docker-compose run --rm tests
```

### Остановить тесты
```bash
docker-compose run tests
```

### Остановить все контейнеры
```bash
docker-compose down
```

### Остановить с удалением volumes
```bash
docker-compose down -v
```

## Автоматическая инициализация

При запуске выполняется инициализация:
1. ✓ Создание базы данных
2. ✓ Применение миграций
3. ✓ Создание superuser (admin/admin123)
4. ✓ Заполнение категорий (15 шт.)
5. ✓ Заполнение городов (10 шт.)
6. ✓ Запуск тестов

## Дополнительно

### Вход в контейнеры

```bash
# Backend
docker-compose exec backend bash

# Database
docker-compose exec db psql -U postgres -d rental_db

# Admin
docker-compose exec admin bash
```

### Полезные команды

```bash
# Миграции
docker-compose exec backend python manage.py migrate

# Создание superuser
docker-compose exec backend python manage.py createsuperuser

# Заполнение городов
docker-compose exec backend python manage.py fill_categories
docker-compose exec backend python manage.py fill_cities

# Тесты
docker-compose exec backend python -m pytest apps/ -v
```

## Настройки окружения

| Переменная             | Значение по умолчанию | Назначение          |
|------------------------|-----------------------|---------------------|
| `DJANGO_SETTINGS_MODULE` | config.settings       | Настройки Django    |
| `POSTGRES_DB`          | rental_db             | Имя базы данных     |
| `POSTGRES_USER`        | postgres              | Администратор БД    |
| `POSTGRES_PASSWORD`    | postgres              | Пароль БД           |

Файл `.env` в корне проекта задаёт значения по умолчанию для
`POSTGRES_PASSWORD` и других переменных, используемых docker-compose.
`.env` не попадает в git (см. `.gitignore`).

## Примечания

- Данные базы данных сохраняются в volume `postgres_data`
- Для полного сброса БД: `docker-compose down -v`
- Файлы-изображения хранятся на локальном диске `./media`
- Статика собирается на локальный диск `./staticfiles`