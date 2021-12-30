"""
asgi config for chessclub project.

It exposes the asgi callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/asgi/
"""

import os

from channels.routing         import ProtocolTypeRouter, URLRouter
from channels.auth            import AuthMiddlewareStack
from chessclub.websocket.urls import ws_urlpatterns

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(URLRouter(ws_urlpatterns))
})