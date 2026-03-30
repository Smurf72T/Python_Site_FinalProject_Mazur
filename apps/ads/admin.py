from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Ad,
    AdImage,
    Category,
    Favorite,
    Message,
    Notification,
    RentalRequest,
    Review,
)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "owner",
        "status",
        "price",
        "views_count",
        "created_at",
    )
    list_filter = ("status", "category", "size")
    search_fields = ("title", "description")
    readonly_fields = (
        "views_count",
        "created_at",
        "updated_at",
        "image_preview",
    )

    # Массовые действия
    actions = ["approve_ads", "reject_ads", "mark_as_rented"]

    def approve_ads(self, request, queryset):
        """Опубликовать выбранные объявления."""
        updated = queryset.update(status="approved")
        self.message_user(request, f"Опубликовано {updated} объявлений.")

    approve_ads.short_description = "✓ Опубликовать выбранные"

    def reject_ads(self, request, queryset):
        """Отклонить выбранные объявления."""
        updated = queryset.update(status="rejected")
        self.message_user(request, f"Отклонено {updated} объявлений.")

    reject_ads.short_description = "✗ Отклонить выбранные"

    def mark_as_rented(self, request, queryset):
        """Отметить выбранные объявления как сданные."""
        updated = queryset.update(status="rented")
        self.message_user(
            request, f"Отмечено как сданные {updated} объявлений."
        )

    mark_as_rented.short_description = "→ Отметить как сданные"

    def image_preview(self, obj):
        """Отображение миниатюры изображения объявления."""
        if obj.image and hasattr(obj.image, "url"):
            try:
                img_html = (
                    '<img src="{}" style="width: 50px; '
                    "height: 50px; object-fit: cover; "
                    'border-radius: 5px;" />'
                )
                return format_html(img_html, obj.image.url)
            except Exception:
                return "Ошибка загрузки"
        return "Нет изображения"

    image_preview.short_description = "Изображение"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("ad", "author", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ad",
        "renter",
        "status",
        "start_date",
        "end_date",
        "total_price",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("ad__title", "renter__username")


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "ad", "is_main", "caption", "created_at")
    list_filter = ("is_main",)
    search_fields = ("ad__title", "caption")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        """Отображение миниатюры изображения."""
        if obj.image and hasattr(obj.image, "url"):
            try:
                img_html = (
                    '<img src="{}" style="width: 50px; '
                    "height: 50px; object-fit: cover; "
                    'border-radius: 5px;" />'
                )
                return format_html(img_html, obj.image.url)
            except Exception:
                return "Ошибка загрузки"
        return "Нет изображения"

    image_preview.short_description = "Изображение"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "ad", "created_at")
    search_fields = ("user__username", "ad__title")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender_username",
        "recipient_username",
        "subject",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read",)
    search_fields = ("sender__username", "recipient__username", "subject")

    def sender_username(self, obj):
        """Имя отправителя."""
        return obj.sender.username if obj.sender else "—"

    sender_username.short_description = "Отправитель"

    def recipient_username(self, obj):
        """Имя получателя."""
        return obj.recipient.username if obj.recipient else "—"

    recipient_username.short_description = "Получатель"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read")
    search_fields = ("user__username", "title")
