#!/bin/bash
set -e

# Переход в директорию приложения
cd /app

# Ожидание готовности базы данных
echo "Waiting for database to be ready..."
while ! python -c "import socket; socket.create_connection(('db', 5432), timeout=1)" 2>/dev/null; do
    sleep 1
done
echo "Database is ready!"

# Применение миграций
echo "Applying database migrations..."
python manage.py migrate --noinput

# Сбор статики
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Запуск инициализации данных (если есть)
if [ -f "/app/scripts/init_data.py" ]; then
    echo "Initializing data..."
    python manage.py shell < /app/scripts/init_data.py
fi

# Запуск gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
