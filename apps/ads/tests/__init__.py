"""
Тесты приложения объявлений (ads).

Модульная структура:
- test_models: Тесты моделей
- test_forms: Тесты форм
- test_views: Тесты представлений
- test_services: Тесты сервисных функций
- base: Базовые классы для тестов
"""
from .test_models import (
    CategoryModelTest,
    AdModelTest,
    ReviewModelTest,
    RentalRequestModelTest,
    AdImageModelTest,
    FavoriteModelTest,
    MessageModelTest,
    NotificationModelTest,
)
from .test_forms import AdFormTest, ReviewFormTest
from .test_views import (
    HomeViewTest,
    AdDetailViewTest,
    AdManagementViewsTest,
    RentalRequestViewsTest,
)
from .test_services import ServicesTest

__all__ = [
    # Models
    'CategoryModelTest',
    'AdModelTest',
    'ReviewModelTest',
    'RentalRequestModelTest',
    'AdImageModelTest',
    'FavoriteModelTest',
    'MessageModelTest',
    'NotificationModelTest',
    # Forms
    'AdFormTest',
    'ReviewFormTest',
    # Views
    'HomeViewTest',
    'AdDetailViewTest',
    'AdManagementViewsTest',
    'RentalRequestViewsTest',
    # Services
    'ServicesTest',
]
