"""
Модели приложения пользователей (users).

Содержит модели для управления профилями пользователей,
их настройками и связанной информацией.
"""

from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    """
    Профиль пользователя.

    Расширяет стандартную модель User дополнительными полями:
    контактной информацией, аватаром, статистикой и рейтингом.
    Создаётся автоматически при регистрации нового пользователя.

    Attributes:
        user: Связь с моделью User (OneToOne).
        phone: Номер телефона.
        location: Местоположение пользователя.
        is_moderator: Флаг модератора.
        avatar: Фотография профиля.
        birth_date: Дата рождения.
        bio: Краткая информация о пользователе.
        is_verified: Флаг подтверждённого пользователя.
        rating: Средний рейтинг на основе отзывов.
        ads_count: Количество объявлений пользователя.
        reviews_count: Количество полученных отзывов.
        member_since: Дата регистрации на сайте.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон"
    )
    location = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Местоположение"
    )
    is_moderator = models.BooleanField(default=False, verbose_name="Модератор")

    # Новые поля
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Дата рождения"
    )
    bio = models.TextField(blank=True, max_length=500, verbose_name="О себе")
    is_verified = models.BooleanField(
        default=False, verbose_name="Подтверждён"
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, verbose_name="Рейтинг"
    )

    # Статистика
    ads_count = models.PositiveIntegerField(
        default=0, verbose_name="Объявлений"
    )
    reviews_count = models.PositiveIntegerField(
        default=0, verbose_name="Отзывов"
    )
    member_since = models.DateTimeField(
        null=True, blank=True, verbose_name="С даты"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        ordering = ["-member_since"]

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_age(self):
        """
        Вычислить возраст пользователя по дате рождения.

        Returns:
            int: Возраст в годах, или None если дата рождения не указана.

        Example:
            >>> profile.birth_date = date(1990, 1, 1)
            >>> profile.get_age()
            36
        """
        if self.birth_date:
            today = date.today()
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )
        return None

    def update_rating(self):
        """
        Обновить рейтинг пользователя на основе отзывов.

        Вычисляет средний рейтинг всех отзывов к объявлениям
        пользователя и обновляет поля rating и reviews_count.

        Example:
            >>> profile.update_rating()
            >>> print(profile.rating)
            4.50
        """
        from apps.ads.models import Review

        # Отзывы к объявлениям пользователя (один запрос к БД)
        stats = Review.objects.filter(ad__owner=self.user).aggregate(
            avg=Avg("rating"), count=Count("id")
        )
        self.rating = stats["avg"] or 0
        self.reviews_count = stats["count"] or 0
        self.save(update_fields=["rating", "reviews_count"])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания профиля.

    Создаёт новый Profile при создании нового User.
    Также устанавливает дату регистрации member_since.

    Args:
        sender: Модель-отправитель (User).
        instance: Экземпляр User.
        created: True если создан новый объект.
        **kwargs: Дополнительные аргументы.
    """
    if created:
        profile = Profile.objects.create(user=instance)
        profile.member_since = timezone.now()
        profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сигнал для автоматического сохранения профиля.

    Сохраняет связанный профиль при сохранении User.

    Args:
        sender: Модель-отправитель (User).
        instance: Экземпляр User.
        **kwargs: Дополнительные аргументы.
    """
    if hasattr(instance, "profile"):
        instance.profile.save()
