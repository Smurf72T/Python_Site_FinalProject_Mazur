#!/bin/bash
# Скрипт инициализации данных при первом запуске контейнера

echo "========================================="
echo "Проверка необходимости наполнения БД..."
echo "========================================="

# Проверяем, пуста ли таблица категорий
CATEGORIES_COUNT=$(python manage.py shell -c "from apps.ads.models import Category; print(Category.objects.count())" 2>/dev/null)

if [ "$CATEGORIES_COUNT" -eq 0 ]; then
    echo ""
    echo "Таблица категорий пуста. Заполняю..."
    python manage.py fill_categories
else
    echo "Таблица категорий уже заполнена ($CATEGORIES_COUNT записей)"
fi

# Проверяем, пуста ли таблица городов
CITIES_COUNT=$(python manage.py shell -c "from apps.ads.models import City; print(City.objects.count())" 2>/dev/null)

if [ "$CITIES_COUNT" -eq 0 ]; then
    echo ""
    echo "Таблица городов пуста. Заполняю..."
    python manage.py fill_cities
else
    echo "Таблица городов уже заполнена ($CITIES_COUNT записей)"
fi

echo ""
echo "========================================="
echo "Инициализация данных завершена!"
echo "========================================="
