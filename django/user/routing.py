from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/fetch_price/$', consumers.MyWebSocketConsumer.as_asgi()),
]

