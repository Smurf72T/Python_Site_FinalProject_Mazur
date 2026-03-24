"""
Базовые настройки и утилиты для тестов приложения users.
"""

import logging
import os

from django.contrib.auth.models import User
from django.test import TestCase

# Настройка логирования для тестов
LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "users_tests.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BaseUsersTestCase(TestCase):
    """
    Базовый класс для тестов приложения users.
    """

    def create_user(self, username="user", password="pass123", **kwargs):
        """Создать пользователя."""
        defaults = {"password": password}
        defaults.update(kwargs)
        return User.objects.create_user(username=username, **defaults)
