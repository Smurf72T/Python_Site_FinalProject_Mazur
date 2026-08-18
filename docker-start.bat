@echo off
chcp 65001 >nul
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

echo [2/4] Ожидание инициализации БД...
timeout /t 10 /nobreak >nul

echo [3/4] Запуск backend...
docker-compose up -d backend admin

echo [4/4] Запуск тестов...
docker-compose up -d tests

echo.
echo ============================================
echo   Запуск завершён!
echo ============================================