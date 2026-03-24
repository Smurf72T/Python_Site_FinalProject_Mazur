#!/bin/bash
set -e

echo "=== Инициализация Django Admin ==="

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
until python manage.py migrate --check 2>/dev/null; do
    echo "База данных ещё не готова. Ожидание..."
    sleep 2
done

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
    print('ℹ Superuser уже существует')
EOF

# Сборка статики
echo "Сборка статики..."
python manage.py collectstatic --noinput

# Запуск сервера админки
echo "Запуск Django Admin сервера на порту 8001..."
exec python manage.py runserver 0.0.0.0:8001
