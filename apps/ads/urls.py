from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_ad, name='create'),
    path('ad/<int:pk>/', views.ad_detail, name='detail'),
    path('ad/<int:pk>/edit/', views.edit_ad, name='edit'),
    path('ad/<int:pk>/delete/', views.delete_ad, name='delete'),
    path('moderate/', views.moderate_ads, name='moderate'),
]