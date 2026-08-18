#!/bin/bash
set -e

echo "=== Инициализация Django Admin ==="

# Ожидание запуска базы данных через Python socket
echo "Ожидание запуска базы данных..."
until python -c "import socket; s=socket.socket(); s.connect(('db', 5432)); s.close()" 2>/dev/null; do
    echo "База данных ещё не доступна. Повторяем..."
    sleep 2
done

echo "База данных доступна!"

# Проверка доступности Django и БД
echo "Проверка доступности Django..."
until python manage.py check > /dev/null 2>&1; do
    echo "Django не смог подключиться к БД. Повторяем..."
    sleep 2
done

echo "Django работает!"

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --noinput

# Создание superuser
echo "Создание superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@admin.admin',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    print('✓ Superuser создан: login=admin, password=admin123')
else:
    print('✓ Superuser уже существует')
EOF

# Сборка статики (удаляем старые файлы перед сборкой)
echo "Сборка статики..."
rm -rf /app/staticfiles/*
python manage.py collectstatic --noinput

# Запуск админки
echo "Запуск Django Admin сервера на порту 8001..."
exec python manage.py runserver 0.0.0.0:8001