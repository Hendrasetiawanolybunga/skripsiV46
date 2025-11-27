from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notifikasi/', consumers.NotificationConsumer.as_asgi()),
]