"""
Тесты приложения пользователей (users).

Модульная структура:
- test_models: Тесты моделей
- test_forms: Тесты форм
- test_views: Тесты представлений
- test_views_extended: Расширенные тесты представлений
- base: Базовые классы для тестов
"""

from .test_forms import ProfileFormTest, RegistrationFormTest
from .test_models import ProfileModelTest
from .test_views import MessageViewsTest, ProfileViewsTest, UserAuthViewsTest
from .test_views_extended import (MessageDetailViewExtendedTest,
                                  MessagesListViewExtendedTest,
                                  ProfileEditViewExtendedTest,
                                  ProfileViewExtendedTest,
                                  RegisterViewExtendedTest)

__all__ = [
    # Models
    "ProfileModelTest",
    # Forms
    "RegistrationFormTest",
    "ProfileFormTest",
    # Views
    "UserAuthViewsTest",
    "ProfileViewsTest",
    "ProfileViewExtendedTest",
    "ProfileEditViewExtendedTest",
    "MessageViewsTest",
    "MessagesListViewExtendedTest",
    "MessageDetailViewExtendedTest",
    "RegisterViewExtendedTest",
]
