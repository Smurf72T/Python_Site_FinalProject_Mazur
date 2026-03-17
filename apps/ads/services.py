from django.db.models import Q
from .models import Ad

def get_filtered_ads(queryset, search=None, location=None, min_price=None, max_price=None):
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
    return queryset

def approve_ad_instance(ad):
    ad.status = 'approved'
    ad.save()
    return ad

def reject_ad_instance(ad):
    ad.status = 'rejected'
    ad.save()
    return ad