.PHONY: test test-quick test-views test-cov test-html lint format clean

# Быстрый запуск основных тестов (модели, формы, сервисы)
test:
	python -m pytest apps/ads/tests/test_models.py \
		apps/ads/tests/test_forms.py \
		apps/ads/tests/test_services.py \
		apps/users/tests/test_models.py \
		apps/users/tests/test_forms.py \
		-v --tb=short

# Быстрый запуск тестов без покрытия
test-quick:
	python -m pytest apps/ads/tests/test_models.py \
		apps/ads/tests/test_forms.py \
		apps/ads/tests/test_services.py \
		apps/users/tests/test_models.py \
		apps/users/tests/test_forms.py \
		-v --tb=short --no-cov

# Запуск тестов views (могут иметь проблемы с pytest-django)
test-views:
	python -m pytest apps/ads/tests/test_views.py apps/users/tests/test_views.py -v --tb=short --no-cov

# Тесты с покрытием в терминале
test-cov:
	python -m pytest apps/ads/tests apps/users/tests -v --tb=short --cov=apps --cov-report=term-missing

# Тесты с HTML-отчётом по покрытию
test-html:
	python -m pytest apps/ads/tests apps/users/tests -v --tb=short --cov=apps --cov-report=html
	@echo "Отчёт сохранён в htmlcov/index.html"

# Проверка кода на PEP8
lint:
	python -m black apps/ config/ --check --exclude migrations
	python -m isort apps/ config/ --check-only --skip migrations
	python -m flake8 apps/ config/ --exclude migrations --max-line-length=120

# Автоформатирование кода
format:
	python -m black apps/ config/ --exclude migrations
	python -m isort apps/ config/ --skip migrations

# Очистка
clean:
	-rmdir /s /q .pytest_cache
	-rmdir /s /q htmlcov
	-rmdir /s /q .mypy_cache
	-del /q *.pyc
	-del /q .coverage