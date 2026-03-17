from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_moderator = models.BooleanField(default=False)
    
    # Новые поля
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    bio = models.TextField(blank=True, max_length=500, verbose_name='О себе')
    is_verified = models.BooleanField(default=False, verbose_name='Подтверждён')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='Рейтинг')
    
    # Статистика
    ads_count = models.PositiveIntegerField(default=0, verbose_name='Объявлений')
    reviews_count = models.PositiveIntegerField(default=0, verbose_name='Отзывов')
    member_since = models.DateTimeField(null=True, blank=True, verbose_name='С даты')

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def get_age(self):
        """Вычислить возраст пользователя"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    def update_rating(self):
        """Обновить рейтинг на основе отзывов к объявлениям пользователя"""
        from apps.ads.models import Review
        # Отзывы к объявлениям пользователя
        reviews = Review.objects.filter(ad__owner=self.user)
        if reviews.exists():
            self.rating = sum(r.rating for r in reviews) / reviews.count()
            self.reviews_count = reviews.count()
            self.save(update_fields=['rating', 'reviews_count'])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    from django.utils import timezone
    if created:
        profile = Profile.objects.create(user=instance)
        profile.member_since = timezone.now()
        profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()