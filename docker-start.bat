@echo off
echo ============================================
echo   Запуск Docker контейнеров Rental Project
echo ============================================
echo.

REM Проверка наличия Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker не найден. Установите Docker Desktop.
    pause
    exit /b 1
)

echo [1/4] Запуск базы данных...
docker-compose up -d db

echo [2/4] Ожидание готовности БД...
timeout /t 10 /nobreak >nul

echo [3/4] Запуск backend...
docker-compose up -d backend admin

echo [4/4] Запуск тестов...
docker-compose up -d tests

echo.
echo ============================================
echo   Запуск завершён!
echo ============================================
echo.
echo Сервисы доступны:
echo   - Backend:    http://localhost:8000
echo   - Admin:      http://localhost:8001/admin/
echo   - Database:   localhost:5432
echo.
echo Логин/пароль администратора:
echo   Login: admin
echo   Password: admin123
echo.
echo Для просмотра логов:
echo   docker-compose logs -f
echo.
echo Для остановки:
echo   docker-compose down
echo ============================================

pause
