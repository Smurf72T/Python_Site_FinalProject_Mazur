"""
Модели социального взаимодействия: избранное, сообщения, уведомления.
"""

from django.contrib.auth.models import User
from django.db import models


class Favorite(models.Model):
    """
    Избранное объявление.

    Пользователи могут добавлять объявления в избранное
    для быстрого доступа.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    ad = models.ForeignKey(
        "Ad",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Объявление",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ["-created_at"]
        unique_together = ["user", "ad"]

    def __str__(self):
        return f"{self.user.username} favorited {self.ad.title}"


class Message(models.Model):
    """
    Сообщение между пользователями.

    Система внутренних сообщений для общения между
    арендатором и владельцем объявления.
    """

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Отправитель",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="Получатель",
    )
    ad = models.ForeignKey(
        "Ad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name="Объявление",
    )

    subject = models.CharField(max_length=200, blank=True, verbose_name="Тема")
    body = models.TextField(verbose_name="Сообщение")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата отправки"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        body_preview = self.body[:50] if self.body else ""
        return (
            f"From {self.sender.username} "
            f"to {self.recipient.username}: {body_preview}"
        )


class Notification(models.Model):
    """
    Уведомление пользователя.

    Система уведомлений для информирования пользователей
    о важных событиях (новые сообщения, статусы заявок и т.д.).
    """

    TYPE_CHOICES = [
        ("info", "Информация"),
        ("warning", "Предупреждение"),
        ("success", "Успех"),
        ("error", "Ошибка"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="info",
        verbose_name="Тип",
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    link = models.CharField(max_length=500, blank=True, verbose_name="Ссылка")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-is_read", "-created_at"]

    def __str__(self):
        return (
            f"[{self.notification_type}] {self.title} for {self.user.username}"
        )

    def mark_as_read(self):
        """
        Отметить уведомление как прочитанное.
        """
        self.is_read = True
        self.save(update_fields=["is_read"])
