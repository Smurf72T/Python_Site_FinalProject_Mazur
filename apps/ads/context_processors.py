from apps.ads.models import Notification


def unread_notifications(request):
    """
    Контекст-процессор для подсчёта непрочитанных уведомлений.

    Не работает для Django Admin во избежание конфликтов.
    """
    # Пропускаем запросы админки
    if hasattr(request, "path") and request.path.startswith("/admin/"):
        return {"unread_count": 0}

    if request.user.is_authenticated:
        return {
            "unread_count": Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        }
    return {"unread_count": 0}
