"""
Тесты для моделей приложения users.
"""
from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import Profile


class ProfileModelTest(TestCase):
    """Тесты для модели Profile."""

    def test_create_profile_on_user_creation(self):
        """Профиль создаётся автоматически при создании пользователя."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)

    def test_profile_string_representation(self):
        """Строковое представление профиля."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(str(user.profile), 'testuser Profile')

    def test_profile_default_values(self):
        """Значения по умолчанию для полей профиля."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.profile.phone, None)
        self.assertEqual(user.profile.location, None)
        self.assertFalse(user.profile.is_moderator)

    def test_profile_new_fields(self):
        """Тест новых полей профиля."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            email='test@example.com'
        )
        profile = user.profile
        profile.bio = 'Люблю моду'
        profile.is_verified = True
        profile.rating = Decimal('4.5')
        profile.save()
        self.assertEqual(profile.bio, 'Люблю моду')
        self.assertTrue(profile.is_verified)
        self.assertEqual(profile.rating, Decimal('4.5'))

    def test_profile_get_age(self):
        """Тест вычисления возраста."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        user.profile.birth_date = date(1990, 1, 1)
        user.profile.save()
        age = user.profile.get_age()
        self.assertIsNotNone(age)
        self.assertGreater(age, 0)

    def test_profile_get_age_no_birthdate(self):
        """Тест возраста без даты рождения."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        user.profile.birth_date = None
        user.profile.save()
        age = user.profile.get_age()
        self.assertIsNone(age)

    def test_profile_update_rating(self):
        """Тест обновления рейтинга."""
        from apps.ads.models import Review, Ad

        owner = User.objects.create_user(username='owner', password='pass')
        reviewer = User.objects.create_user(username='reviewer', password='pass')

        image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        ad = Ad.objects.create(
            owner=owner,
            title='Тест',
            description='Описание',
            price=Decimal('1000.00'),
            location='Москва',
            image=image
        )

        Review.objects.create(ad=ad, author=reviewer, rating=5, comment='Отлично')
        Review.objects.create(ad=ad, author=reviewer, rating=4, comment='Хорошо')

        owner.profile.update_rating()
        self.assertEqual(owner.profile.rating, Decimal('4.50'))
        self.assertEqual(owner.profile.reviews_count, 2)

    def test_profile_statistics(self):
        """Тест статистики профиля."""
        user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        self.assertEqual(user.profile.ads_count, 0)
        self.assertEqual(user.profile.reviews_count, 0)
        self.assertIsNotNone(user.profile.member_since)
