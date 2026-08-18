#!/bin/bash
set -e

echo "============================================"
echo "  Запуск автоматических тестов"
echo "============================================"

# Ожидание миграций базы данных
echo "Ожидание миграций базы данных..."
max_attempts=30
attempt=0

until python manage.py migrate --check 2>/dev/null; do
    attempt=$((attempt + 1))
    echo "База данных ещё не готова. Попытка $attempt/$max_attempts..."
    if [ $attempt -ge $max_attempts ]; then
        echo "✗ Превышено время ожидания базы данных"
        exit 1
    fi
    sleep 2
done

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --noinput

# Запуск тестов
echo ""
echo "============================================"
echo "  Запуск pytest"
echo "============================================"
echo ""

# Запуск тестов с отчетом
python -m pytest \
    apps/ads/tests/test_models.py \
    apps/ads/tests/test_forms.py \
    apps/ads/tests/test_services.py \
    apps/ads/tests/test_views.py \
    apps/ads/tests/test_views_extended.py \
    apps/ads/tests/test_extras.py \
    apps/users/tests/test_models.py \
    apps/users/tests/test_forms.py \
    apps/users/tests/test_views.py \
    apps/users/tests/test_views_extended.py \
    -v \
    --tb=short \
    --cov=apps \
    --cov-report=html:/app/test_results/htmlcov \
    --cov-report=term-missing \
    --no-migrations \
    -p no:warnings

TEST_RESULT=$?

echo ""
echo "============================================"
echo "  Результат тестов"
echo "============================================"
echo ""

if [ $TEST_RESULT -eq 0 ]; then
    echo "✓ Все тесты пройдены!"
else
    echo "✗ Некоторые тесты не пройдены (код выхода: $TEST_RESULT)"
fi

echo ""
echo "◈ Отчёт покрытия: /app/test_results/htmlcov/index.html"
echo "◈ HTML отчёт: /app/test_results/report.html"
echo ""

# Отображение результата
echo "============================================"
echo "  Покрытие кода"
echo "============================================"

# Возвращаем код с результатом тестов
exit $TEST_RESULT