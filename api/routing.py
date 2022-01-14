from django.urls import re_path
from .views import v_sock

websocket_urlpatterns = [
    re_path(r'ws/um/(?P<u_id>[0-9]{7})$', v_sock.UmConsumer.as_asgi()),
]