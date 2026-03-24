"""
Тесты приложения пользователей (users).

Модульная структура:
- test_models: Тесты моделей
- test_forms: Тесты форм
- test_views: Тесты представлений
- base: Базовые классы для тестов
"""
from .test_models import ProfileModelTest
from .test_forms import RegistrationFormTest, ProfileFormTest
from .test_views import UserAuthViewsTest, ProfileViewsTest, MessageViewsTest

__all__ = [
    # Models
    'ProfileModelTest',
    # Forms
    'RegistrationFormTest',
    'ProfileFormTest',
    # Views
    'UserAuthViewsTest',
    'ProfileViewsTest',
    'MessageViewsTest',
]
