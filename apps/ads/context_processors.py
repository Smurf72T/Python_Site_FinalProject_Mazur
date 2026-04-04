def unread_notifications(request):
    """
    Контекст-процессор для подсчёта непрочитанных уведомлений.

    Не работает для Django Admin во избежание конфликтов с pytest-django.
    """
    # Пропускаем запросы админки - проверяем path и resolver
    if hasattr(request, "path") and request.path.startswith("/admin/"):
        return {"unread_count": 0}

    # Дополнительная проверка - не админский ли это запрос
    if hasattr(request, "resolver_match"):
        if (
            request.resolver_match
            and request.resolver_match.app_name == "admin"
        ):
            return {"unread_count": 0}

    if request.user.is_authenticated:
        try:
            from apps.ads.models import Notification

            return {
                "unread_count": Notification.objects.filter(
                    user=request.user, is_read=False
                ).count()
            }
        except Exception:
            # В случае ошибки (например в админке) возвращаем 0
            pass

    return {"unread_count": 0}
