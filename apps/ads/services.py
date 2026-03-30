from django.db.models import Q


def get_filtered_ads(
    queryset,
    search=None,
    location=None,
    min_price=None,
    max_price=None,
    category=None,
    city=None,
):
    """
    Фильтрация объявлений по параметрам.

    Args:
        queryset: Исходный queryset объявлений
        search: Поиск по названию и описанию
        location: Фильтр по району/метро
        min_price: Минимальная цена
        max_price: Максимальная цена
        category: ID категории
        city: ID города

    Returns:
        Отфильтрованный queryset
    """
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    if location:
        queryset = queryset.filter(location__icontains=location)
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if category:
        queryset = queryset.filter(category_id=category)
    if city:
        queryset = queryset.filter(city_id=city)
    return queryset


def approve_ad_instance(ad):
    ad.status = "approved"
    ad.save()
    return ad


def reject_ad_instance(ad):
    ad.status = "rejected"
    ad.save()
    return ad
