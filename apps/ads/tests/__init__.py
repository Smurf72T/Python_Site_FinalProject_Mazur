"""
Тесты приложения объявлений (ads).

Модульная структура:
- test_models: Тесты моделей
- test_forms: Тесты форм
- test_views: Тесты представлений
- test_services: Тесты сервисных функций
- base: Базовые классы для тестов
"""

from .test_forms import AdFormTest, ReviewFormTest
from .test_models import (AdImageModelTest, AdModelTest, CategoryModelTest,
                          FavoriteModelTest, MessageModelTest,
                          NotificationModelTest, RentalRequestModelTest,
                          ReviewModelTest)
from .test_services import ServicesTest
from .test_views import (AdDetailViewTest, AdManagementViewsTest, HomeViewTest,
                         RentalRequestViewsTest)

__all__ = [
    # Models
    "CategoryModelTest",
    "AdModelTest",
    "ReviewModelTest",
    "RentalRequestModelTest",
    "AdImageModelTest",
    "FavoriteModelTest",
    "MessageModelTest",
    "NotificationModelTest",
    # Forms
    "AdFormTest",
    "ReviewFormTest",
    # Views
    "HomeViewTest",
    "AdDetailViewTest",
    "AdManagementViewsTest",
    "RentalRequestViewsTest",
    # Services
    "ServicesTest",
]
