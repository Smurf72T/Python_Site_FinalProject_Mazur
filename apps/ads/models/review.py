"""
Модель отзыва об объявлении.
"""

from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    """
    Отзыв об объявлении.

    Пользователи могут оставлять отзывы и оценки к объявлениям.
    Рейтинг влияет на общий рейтинг владельца объявления.
    """

    ad = models.ForeignKey(
        "Ad",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Объявление",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], verbose_name="Рейтинг"
    )
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.author.username} on {self.ad.title}"

    def save(self, *args, **kwargs):
        """
        Сохранить отзыв и обновить рейтинг владельца объявления.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ad.owner.profile.update_rating()
