from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "location",
        "is_moderator",
        "is_verified",
        "rating",
        "ads_count",
        "reviews_count",
        "member_since",
    )
    list_editable = ("is_moderator", "is_verified")
    list_filter = ("is_moderator", "is_verified")
    search_fields = ("user__username", "phone", "location")
    readonly_fields = ("rating", "ads_count", "reviews_count", "member_since")
