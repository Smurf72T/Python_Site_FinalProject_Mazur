from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ad(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Опубликовано'),
        ('rejected', 'Отклонено'),
        ('rented', 'Сдано'),
    ]

    SIZE_CHOICES = [
        ('XS', 'XS (40-42)'),
        ('S', 'S (42-44)'),
        ('M', 'M (44-46)'),
        ('L', 'L (46-48)'),
        ('XL', 'XL (48-50)'),
        ('XXL', 'XXL (50-52)'),
        ('XXXL', 'XXXL (52+)'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Залог')
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads_images/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Даты аренды
    rental_start_date = models.DateField(null=True, blank=True, verbose_name='Начало аренды')
    rental_end_date = models.DateField(null=True, blank=True, verbose_name='Окончание аренды')
    min_rental_days = models.PositiveIntegerField(default=1, verbose_name='Мин. срок аренды (дней)')
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_available(self):
        """Проверка доступности объявления"""
        if self.status != 'approved':
            return False
        if self.rental_end_date and self.rental_end_date < timezone.now().date():
            return False
        return True

    def increment_views(self):
        """Увеличить счётчик просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

class Review(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author.username} on {self.ad.title}"
    
    def save(self, *args, **kwargs):
        """Обновить рейтинг владельца объявления при сохранении отзыва"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ad.owner.profile.update_rating()


# ============================================================
# НОВЫЕ МОДЕЛИ
# ============================================================

class RentalRequest(models.Model):
    """Заявка на аренду одежды"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Подтверждено'),
        ('rejected', 'Отклонено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='rental_requests')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_requests')
    
    # Даты аренды
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    
    # Статус и информация
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['ad', 'renter', 'start_date', 'end_date']

    def __str__(self):
        return f"Request #{self.id} - {self.ad.title} ({self.renter.username})"
    
    def calculate_total_price(self):
        """Рассчитать общую стоимость аренды"""
        days = (self.end_date - self.start_date).days + 1
        if days < self.ad.min_rental_days:
            days = self.ad.min_rental_days
        return self.ad.price * days
    
    def save(self, *args, **kwargs):
        """Автоматический расчёт стоимости при сохранении"""
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class AdImage(models.Model):
    """Дополнительные изображения объявления"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ads_images/gallery/')
    caption = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    is_main = models.BooleanField(default=False, verbose_name='Основное фото')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', '-created_at']

    def __str__(self):
        return f"Image for {self.ad.title}"
    
    def save(self, *args, **kwargs):
        """Если изображение основное, убрать флаг у остальных"""
        if self.is_main:
            AdImage.objects.filter(ad=self.ad, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """Избранные объявления"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'ad']

    def __str__(self):
        return f"{self.user.username} favorited {self.ad.title}"


class Message(models.Model):
    """Сообщения между пользователями"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    ad = models.ForeignKey(Ad, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    
    subject = models.CharField(max_length=200, blank=True, verbose_name='Тема')
    body = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.body[:50]}"


class Notification(models.Model):
    """Уведомления пользователей"""
    TYPE_CHOICES = [
        ('info', 'Информация'),
        ('warning', 'Предупреждение'),
        ('success', 'Успех'),
        ('error', 'Ошибка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    link = models.CharField(max_length=500, blank=True, verbose_name='Ссылка')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_read', '-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} for {self.user.username}"
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        self.is_read = True
        self.save(update_fields=['is_read'])