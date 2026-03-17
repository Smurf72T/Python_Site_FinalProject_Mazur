from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ad, Review
from .forms import AdForm, ReviewForm
from .services import get_filtered_ads, approve_ad_instance, reject_ad_instance

def home(request):
    ads = Ad.objects.filter(status='approved')
    search = request.GET.get('search')
    location = request.GET.get('location')
    ads = get_filtered_ads(ads, search, location)
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
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ad = ad
            review.author = request.user
            review.save()
            return redirect('ads:detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'ads/detail.html', {'ad': ad, 'form': form})