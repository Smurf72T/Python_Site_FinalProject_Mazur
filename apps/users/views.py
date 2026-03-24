from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, ProfileForm
from apps.ads.models import Ad, RentalRequest


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('ads:home')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """
    Страница профиля пользователя с отображением информации и объявлений.
    """
    ads = Ad.objects.filter(owner=request.user).order_by('-created_at')
    
    # Арендованные объявления (где пользователь - арендатор с подтверждённой заявкой)
    rented_ads = RentalRequest.objects.filter(
        renter=request.user, 
        status='accepted'
    ).select_related('ad').order_by('-start_date')
    
    return render(request, 'registration/profile.html', {
        'user': request.user, 
        'ads': ads,
        'rented_ads': rented_ads
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    ads = Ad.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'registration/profile_edit.html', {'form': form, 'ads': ads})