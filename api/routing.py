from django.conf.urls import url
from . import views_sock

websocket_urlpatterns = [
    url(r'ws/um', views_sock.UmConsumer.as_asgi()),
]