from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Ad, Review, RentalRequest, Notification
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
    
    # Проверка: пользователь не может арендовать своё объявление
    if ad.owner == request.user:
        messages.error(request, 'Это ваше объявление. Нельзя арендовать собственное объявление.')
        return redirect('ads:detail', pk=pk)
    
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
                
                # Создаём уведомление для владельца
                Notification.objects.create(
                    user=ad.owner,
                    title='Новая заявка на аренду',
                    message=f'Пользователь {request.user.username} хочет арендовать ваше объявление "{ad.title}". '
                            f'Период: {start_date} - {end_date}.',
                    notification_type='info',
                    link=f'/ads/requests/{rental_request.id}/'
                )
                
                messages.success(request, 'Заявка на аренду создана.')
                return redirect('ads:detail', pk=pk)
        else:
            messages.error(request, 'Укажите даты аренды.')
    
    return redirect('ads:detail', pk=pk)


@login_required
def my_requests(request):
    """
    Страница моих заявок на аренду.
    """
    # Заявки, где пользователь - арендатор
    renter_requests = RentalRequest.objects.filter(renter=request.user).order_by('-created_at')
    
    # Заявки на объявления пользователя (где он владелец)
    owner_requests = RentalRequest.objects.filter(ad__owner=request.user).order_by('-created_at')
    
    return render(request, 'ads/my_requests.html', {
        'renter_requests': renter_requests,
        'owner_requests': owner_requests
    })


@login_required
def request_detail(request, pk):
    """
    Страница детали заявки на аренду.
    """
    rental_request = get_object_or_404(RentalRequest, pk=pk)
    
    # Доступ только для владельца объявления или арендатора
    if rental_request.ad.owner != request.user and rental_request.renter != request.user:
        messages.error(request, 'Доступ запрещён.')
        return redirect('ads:home')
    
    return render(request, 'ads/request_detail.html', {'rental_request': rental_request})


@login_required
def respond_to_request(request, pk):
    """
    Ответ на заявку на аренду (подтвердить/отклонить).
    """
    rental_request = get_object_or_404(RentalRequest, pk=pk)
    
    # Доступ только для владельца объявления
    if rental_request.ad.owner != request.user:
        messages.error(request, 'Доступ запрещён.')
        return redirect('ads:home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            rental_request.status = 'accepted'
            rental_request.save()
            
            # Меняем статус объявления на 'rented'
            rental_request.ad.status = 'rented'
            rental_request.ad.save()
            
            # Уведомление арендатору
            Notification.objects.create(
                user=rental_request.renter,
                title='Заявка подтверждена',
                message=f'Ваша заявка на аренду "{rental_request.ad.title}" подтверждена! '
                        f'Период: {rental_request.start_date} - {rental_request.end_date}.',
                notification_type='success',
                link=f'/ad/{rental_request.ad.pk}/'
            )
            
            messages.success(request, 'Заявка подтверждена. Объявление отмечено как сданное.')
            
        elif action == 'reject':
            rental_request.status = 'rejected'
            rental_request.save()
            
            # Уведомление арендатору
            Notification.objects.create(
                user=rental_request.renter,
                title='Заявка отклонена',
                message=f'Ваша заявка на аренду "{rental_request.ad.title}" отклонена.',
                notification_type='error',
                link=f'/ad/{rental_request.ad.pk}/'
            )
            
            messages.success(request, 'Заявка отклонена.')
    
    return redirect('ads:my_requests')


@login_required
def send_message(request, recipient_id):
    """
    Отправить сообщение пользователю.
    """
    from django.contrib.auth.models import User
    from .models import Message
    
    recipient = get_object_or_404(User, pk=recipient_id)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        subject = request.POST.get('subject', '')
        ad_id = request.POST.get('ad_id')
        
        if body:
            ad = get_object_or_404(Ad, pk=ad_id) if ad_id else None
            
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                ad=ad
            )
            
            # Уведомление о новом сообщении
            Notification.objects.create(
                user=recipient,
                title='Новое сообщение',
                message=f'Вам отправили сообщение от {request.user.username}',
                notification_type='info',
                link='/users/messages/'
            )
            
            messages.success(request, 'Сообщение отправлено.')
            return redirect('ads:my_requests')
    
    return redirect('ads:my_requests')