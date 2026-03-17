import logging
import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal
from .models import Profile
from .forms import RegistrationForm, ProfileForm

# Настройка логирования для тестов
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'users_tests.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfileModelTest(TestCase):
    """Тесты для модели Profile"""

    def test_create_profile_on_user_creation(self):
        """Профиль создаётся автоматически при создании пользователя"""
        logger.info("Начало теста: создание профиля при создании пользователя")
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        logger.info(f"Создан пользователь {user.username}, профиль: {hasattr(user, 'profile')}")
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)

    def test_profile_string_representation(self):
        """Строковое представление профиля"""
        logger.info("Начало теста: строковое представление профиля")
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        logger.info(f"Проверка str(profile) для {user.username}")
        self.assertEqual(str(user.profile), 'testuser Profile')

    def test_profile_default_values(self):
        """Значения по умолчанию для полей профиля"""
        logger.info("Начало теста: значения по умолчанию профиля")
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        logger.debug(f"phone={user.profile.phone}, location={user.profile.location}, is_moderator={user.profile.is_moderator}")
        self.assertEqual(user.profile.phone, None)
        self.assertEqual(user.profile.location, None)
        self.assertFalse(user.profile.is_moderator)


class RegistrationFormTest(TestCase):
    """Тесты для формы регистрации"""

    def test_registration_form_valid(self):
        """Валидная форма регистрации"""
        logger.info("Начало теста: валидная форма регистрации")
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = RegistrationForm(data=form_data)
        logger.info(f"Форма валидна: {form.is_valid()}")
        self.assertTrue(form.is_valid())

    def test_registration_form_saves_email(self):
        """Форма сохраняет email пользователя"""
        logger.info("Начало теста: сохранение email")
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = RegistrationForm(data=form_data)
        user = form.save()
        logger.info(f"Сохранён пользователь {user.username} с email {user.email}")
        self.assertEqual(user.email, 'newuser@example.com')

    def test_registration_form_password_mismatch(self):
        """Несовпадение паролей"""
        logger.info("Начало теста: несовпадение паролей")
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!'
        }
        form = RegistrationForm(data=form_data)
        logger.info(f"Форма валидна: {form.is_valid()}, ошибки: {form.errors.keys()}")
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_form_weak_password(self):
        """Слабый пароль"""
        logger.info("Начало теста: слабый пароль")
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',
            'password2': '123'
        }
        form = RegistrationForm(data=form_data)
        logger.info(f"Форма валидна: {form.is_valid()}, ошибки: {form.errors.keys()}")
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_form_duplicate_username(self):
        """Дубликат имени пользователя"""
        logger.info("Начало теста: дубликат username")
        User.objects.create_user(username='existing', password='pass')
        form_data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = RegistrationForm(data=form_data)
        logger.info(f"Форма валидна: {form.is_valid()}, ошибки: {form.errors.keys()}")
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class ProfileFormTest(TestCase):
    """Тесты для формы профиля"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_profile_form_valid(self):
        """Валидная форма профиля"""
        form_data = {
            'phone': '+7 999 123-45-67',
            'location': 'Москва'
        }
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.phone, '+7 999 123-45-67')
        self.assertEqual(profile.location, 'Москва')

    def test_profile_form_empty(self):
        """Форма профиля с пустыми значениями"""
        form_data = {
            'phone': '',
            'location': ''
        }
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())


class UserAuthViewsTest(TestCase):
    """Тесты для представлений аутентификации"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_register_view_get(self):
        """Страница регистрации GET"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post_valid(self):
        """Регистрация с валидными данными"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = self.client.post(reverse('users:register'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Страница входа GET"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_valid(self):
        """Вход с валидными данными"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_invalid(self):
        """Вход с неверными данными"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Выход из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated(self):
        """Страница профиля для авторизованного"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        """Страница профиля для неавторизованного"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_post(self):
        """Редактирование профиля POST"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:profile'), {
            'phone': '+7 999 123-45-67',
            'location': 'Москва'
        })
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '+7 999 123-45-67')
        self.assertEqual(self.user.profile.location, 'Москва')


# ============================================================
# ТЕСТЫ ДЛЯ РАСШИРЕННОЙ МОДЕЛИ PROFILE
# ============================================================

class ProfileExtendedModelTest(TestCase):
    """Расширенные тесты для модели Profile"""

    def setUp(self):
        logger.info("SetUp: создание пользователя для тестов профиля")
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            email='test@example.com'
        )
        self.profile = self.user.profile

    def test_profile_new_fields(self):
        """Тест новых полей профиля"""
        logger.info("Начало теста: новые поля профиля")
        self.profile.bio = 'Люблю моду'
        self.profile.is_verified = True
        self.profile.rating = Decimal('4.5')
        self.profile.save()
        logger.debug(f"bio: {self.profile.bio}, is_verified: {self.profile.is_verified}, rating: {self.profile.rating}")
        self.assertEqual(self.profile.bio, 'Люблю моду')
        self.assertTrue(self.profile.is_verified)
        self.assertEqual(self.profile.rating, Decimal('4.5'))

    def test_profile_get_age(self):
        """Тест вычисления возраста"""
        logger.info("Начало теста: вычисление возраста")
        self.profile.birth_date = date(1990, 1, 1)
        self.profile.save()
        age = self.profile.get_age()
        logger.info(f"Возраст пользователя: {age}")
        self.assertIsNotNone(age)
        self.assertGreater(age, 0)

    def test_profile_get_age_no_birthdate(self):
        """Тест возраста без даты рождения"""
        logger.info("Начало теста: возраст без даты рождения")
        self.profile.birth_date = None
        self.profile.save()
        age = self.profile.get_age()
        logger.debug(f"Возраст при отсутствии даты рождения: {age}")
        self.assertIsNone(age)

    def test_profile_update_rating(self):
        """Тест обновления рейтинга"""
        logger.info("Начало теста: обновление рейтинга")
        from apps.ads.models import Review, Ad
        from django.core.files.uploadedfile import SimpleUploadedFile
        from decimal import Decimal
        
        image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        # Создаём объявление от другого пользователя, чтобы отзывы были для self.user
        other_user = User.objects.create_user(username='owner', password='pass')
        ad = Ad.objects.create(
            owner=other_user,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=image
        )
        # self.user оставляет отзывы на объявление - рейтинг должен обновиться у other_user.profile
        Review.objects.create(ad=ad, author=self.user, rating=5, comment='Отлично')
        Review.objects.create(ad=ad, author=self.user, rating=4, comment='Хорошо')
        logger.debug("Создано 2 отзыва с рейтингами 5 и 4")
        
        # Обновляем рейтинг владельца объявления
        other_user.profile.update_rating()
        logger.info(f"Обновлённый рейтинг владельца: {other_user.profile.rating}")
        self.assertEqual(other_user.profile.rating, Decimal('4.50'))
        self.assertEqual(other_user.profile.reviews_count, 2)

    def test_profile_statistics(self):
        """Тест статистики профиля"""
        logger.info("Начало теста: статистика профиля")
        logger.debug(f"ads_count: {self.profile.ads_count}, reviews_count: {self.profile.reviews_count}")
        self.assertEqual(self.profile.ads_count, 0)
        self.assertEqual(self.profile.reviews_count, 0)
        self.assertIsNotNone(self.profile.member_since)
