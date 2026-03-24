@echo off
REM Скрипт для автоматического запуска тестов с pytest

echo ========================================
echo Запуск тестов через pytest
echo ========================================

REM Запуск тестов моделей, форм и сервисов (стабильные тесты)
python -m pytest apps/ads/tests/test_models.py ^
             apps/ads/tests/test_forms.py ^
             apps/ads/tests/test_services.py ^
             apps/users/tests/test_models.py ^
             apps/users/tests/test_forms.py ^
             -v --tb=short --cov=apps --cov-report=html --cov-report=term-missing %*

echo.
echo ========================================
echo Отчёт о покрытии доступен в htmlcov/index.html
echo ========================================
