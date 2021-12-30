
from django.urls import path

from games.views import WebSocketGameRouter
from social.views import WebSocketSocialRouter
from channels.routing import URLRouter

ws_urlpatterns = [
    WebSocketGameRouter().get_ws_include(),
    WebSocketSocialRouter().get_ws_include(),
]
