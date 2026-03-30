from django.urls import path

from . import views

app_name = "ads"

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_ad, name="create"),
    path("ad/<int:pk>/", views.ad_detail, name="detail"),
    path(
        "ad/<int:pk>/rent/",
        views.create_rental_request,
        name="create_rental_request",
    ),
    path("ad/<int:pk>/edit/", views.edit_ad, name="edit"),
    path("ad/<int:pk>/delete/", views.delete_ad, name="delete"),
    path("ad/<int:pk>/rented/", views.mark_as_rented, name="rented"),
    path("moderate/", views.moderate_ads, name="moderate"),
    path("requests/", views.my_requests, name="my_requests"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path(
        "requests/<int:pk>/respond/",
        views.respond_to_request,
        name="respond_to_request",
    ),
    path(
        "message/<int:recipient_id>/", views.send_message, name="send_message"
    ),
]
