"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/

添加channels 支持：
https://channels.readthedocs.io/en/latest/installation.html
"""

import os
import django
import channels.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()
app = channels.routing.get_default_application()
