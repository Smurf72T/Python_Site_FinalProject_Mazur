#!/bin/sh
set -e

echo "========================================="
echo "Запуск инициализации данных..."
echo "========================================="

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
while ! python manage.py check --database default 2>/dev/null; do
    echo "База данных ещё не готова, жду..."
    sleep 2
done

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --noinput

# Инициализация данных (категории и города)
echo "Инициализация данных..."
python manage.py init_data

# Сборка статики
echo "Сборка статики..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "========================================="
echo "Запуск gunicorn..."
echo "========================================="

exec gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
