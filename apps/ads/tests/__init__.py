"""
Тесты приложения объявлений (ads).

Модульная структура:
- test_models: Тесты моделей
- test_forms: Тесты форм
- test_views: Тесты представлений
- test_views_extended: Расширенные тесты представлений
- test_services: Тесты сервисных функций
- test_extras: Тесты context_processors, templatetags, management commands
- base: Базовые классы для тестов
"""

from .test_extras import (DaysBetweenTemplateTest, FillCategoriesCommandTest,
                          FillCitiesCommandTest, InitDataCommandTest,
                          UnreadNotificationsContextProcessorTest)
from .test_forms import AdFormTest, ReviewFormTest
from .test_models import (AdImageModelTest, AdModelTest, CategoryModelTest,
                          FavoriteModelTest, MessageModelTest,
                          NotificationModelTest, RentalRequestModelTest,
                          ReviewModelTest)
from .test_services import ServicesTest
from .test_views import (AdDetailViewTest, AdManagementViewsTest, HomeViewTest,
                         RentalRequestViewsTest)
from .test_views_extended import (AdDetailViewExtendedTest,
                                  AdManagementViewsExtendedTest,
                                  HomeViewExtendedTest,
                                  ModerateViewsExtendedTest,
                                  RentalRequestViewsExtendedTest,
                                  SendMessageViewTest)

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
    "HomeViewExtendedTest",
    "AdDetailViewTest",
    "AdDetailViewExtendedTest",
    "AdManagementViewsTest",
    "AdManagementViewsExtendedTest",
    "ModerateViewsExtendedTest",
    "RentalRequestViewsTest",
    "RentalRequestViewsExtendedTest",
    "SendMessageViewTest",
    # Services
    "ServicesTest",
    # Extras
    "UnreadNotificationsContextProcessorTest",
    "DaysBetweenTemplateTest",
    "InitDataCommandTest",
    "FillCategoriesCommandTest",
    "FillCitiesCommandTest",
]
