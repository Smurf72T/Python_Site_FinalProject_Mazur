from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Ad, Review, RentalRequest
from .forms import AdForm, ReviewForm
from .services import get_filtered_ads, approve_ad_instance, reject_ad_instance

def home(request):
    ads = Ad.objects.filter(status='approved').order_by('-created_at')
    search = request.GET.get('search')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    ads = get_filtered_ads(ads, search, location, min_price, max_price)
    paginator = Paginator(ads, 6)
    page = request.GET.get('page')
    ads = paginator.get_page(page)
    return render(request, 'ads/home.html', {'ads': ads})

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.owner = request.user
            ad.save()
            messages.success(request, 'Объявление отправлено на модерацию.')
            return redirect('ads:home')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})

@login_required
def edit_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено.')
            return redirect('ads:home')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/edit_ad.html', {'form': form})

@login_required
def delete_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk, owner=request.user)
    ad.delete()
    messages.success(request, 'Объявление удалено.')
    return redirect('ads:home')

@login_required
def mark_as_rented(request, pk):
    ad = get_object_or_404(Ad, pk=pk, owner=request.user)
    ad.status = 'rented'
    ad.save()
    messages.success(request, 'Объявление отмечено как сданное.')
    return redirect('ads:home')

@login_required
def moderate_ads(request):
    if not request.user.profile.is_moderator:
        return redirect('ads:home')
    ads = Ad.objects.filter(status='pending')
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        action = request.POST.get('action')
        ad = get_object_or_404(Ad, pk=ad_id)
        if action == 'approve':
            approve_ad_instance(ad)
        elif action == 'reject':
            reject_ad_instance(ad)
        return redirect('ads:moderate')
    return render(request, 'ads/moderate.html', {'ads': ads})

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        if ad.owner == request.user:
            messages.error(request, 'Нельзя оставить отзыв на своё объявление.')
            return redirect('ads:detail', pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ad = ad
            review.author = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен.')
            return redirect('ads:detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'ads/detail.html', {'ad': ad, 'form': form})


@login_required
def create_rental_request(request, pk):
    """
    Создать заявку на аренду объявления.
    """
    ad = get_object_or_404(Ad, pk=pk)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        comment = request.POST.get('comment', '')
        
        if start_date and end_date:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                messages.error(request, 'Дата начала не может быть позже даты окончания.')
            else:
                rental_request = RentalRequest(
                    ad=ad,
                    renter=request.user,
                    start_date=start,
                    end_date=end,
                    comment=comment
                )
                rental_request.save()
                messages.success(request, 'Заявка на аренду создана.')
                return redirect('ads:detail', pk=pk)
        else:
            messages.error(request, 'Укажите даты аренды.')
    
    return redirect('ads:detail', pk=pk)