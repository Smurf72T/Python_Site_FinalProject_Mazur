from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max
from .forms import RegistrationForm, ProfileForm
from apps.ads.models import Ad, RentalRequest, Message


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
    
    # Сданные объявления (где пользователь - владелец, и есть подтверждённая заявка)
    rented_out_ads = RentalRequest.objects.filter(
        ad__owner=request.user,
        status='accepted'
    ).select_related('ad', 'renter').order_by('-start_date')
    
    return render(request, 'registration/profile.html', {
        'user': request.user, 
        'ads': ads,
        'rented_ads': rented_ads,
        'rented_out_ads': rented_out_ads
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


@login_required
def messages_list(request):
    """
    Список сообщений (входящие/исходящие).
    """
    # Получаем все диалоги пользователя
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(recipient=request.user)
    
    # Группируем по собеседникам
    conversations = {}
    
    for msg in sent_messages:
        key = msg.recipient.id
        if key not in conversations:
            conversations[key] = {
                'user': msg.recipient,
                'last_message': msg,
                'unread_count': 0
            }
        if msg.created_at > conversations[key]['last_message'].created_at:
            conversations[key]['last_message'] = msg
    
    for msg in received_messages:
        key = msg.sender.id
        if key not in conversations:
            conversations[key] = {
                'user': msg.sender,
                'last_message': msg,
                'unread_count': 0
            }
        if msg.created_at > conversations[key]['last_message'].created_at:
            conversations[key]['last_message'] = msg
        if not msg.is_read:
            conversations[key]['unread_count'] += 1
    
    # Сортируем по дате последнего сообщения
    conversations_list = sorted(
        conversations.values(),
        key=lambda x: x['last_message'].created_at,
        reverse=True
    )
    
    return render(request, 'registration/messages.html', {
        'conversations': conversations_list
    })


@login_required
def message_detail(request, user_id):
    """
    Просмотр диалога с конкретным пользователем.
    """
    other_user = get_object_or_404(User, pk=user_id)
    
    # Получаем все сообщения между пользователями
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')
    
    # Помечаем входящие сообщения как прочитанные
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        subject = request.POST.get('subject', '')
        ad_id = request.POST.get('ad_id')
        
        if body:
            ad = get_object_or_404(Ad, pk=ad_id) if ad_id else None
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                subject=subject,
                body=body,
                ad=ad
            )
            return redirect('users:message_detail', user_id=user_id)
    
    return render(request, 'registration/message_detail.html', {
        'other_user': other_user,
        'messages': messages
    })