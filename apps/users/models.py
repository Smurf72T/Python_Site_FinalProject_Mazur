"""
Модели приложения пользователей (users).

Содержит модели для управления профилями пользователей,
их настройками и связанной информацией.
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count, DecimalField, PositiveIntegerField, Subquery
from django.db.models.functions import Coalesce
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
            >>> profile = Profile(birth_date=date(2000, 1, 1))
            >>> isinstance(profile.get_age(), int)
            True
            >>> Profile().get_age() is None
            True
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

        Рейтинг пересчитывается одним атомарным UPDATE-запросом
        с подзапросом, чтобы исключить потерю обновлений при
        параллельных отзывах.
        """
        from apps.ads.models import Review

        stats = (
            Review.objects.filter(ad__owner=self.user)
            .values("ad__owner")
            .annotate(avg=Avg("rating"), cnt=Count("id"))
        )

        Profile.objects.filter(pk=self.pk).update(
            rating=Coalesce(
                Subquery(
                    stats.values("avg")[:1],
                    output_field=DecimalField(max_digits=3, decimal_places=2),
                ),
                Decimal("0"),
            ),
            reviews_count=Coalesce(
                Subquery(
                    stats.values("cnt")[:1],
                    output_field=PositiveIntegerField(),
                ),
                0,
            ),
        )
        self.refresh_from_db(fields=["rating", "reviews_count"])


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
