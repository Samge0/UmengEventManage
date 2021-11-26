"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/

添加channels 支持：
https://channels.readthedocs.io/en/latest/installation.html
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import api

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # 配置sock路由地址
            api.urls.websocket_urlpatterns
        )
    ),
})