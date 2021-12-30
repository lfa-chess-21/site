"""chessclub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings

from django.urls import path

from         api.views import ApiRouter
from        home.views import HomeRouter
from       games.views import GamesRouter
from      social.views import SocialRouter
from     account.views import AccountRouter
from tournaments.views import TournamentsRouter

urlpatterns = [
    path('admin/', admin.site.urls),
    ApiRouter().get_include(),
    HomeRouter().get_include(),
    AccountRouter().get_include(),
    GamesRouter().get_include(),
    TournamentsRouter().get_include(),
    SocialRouter().get_include()
]


if settings.DEBUG:
    # Allow custom static file serving (use with manage.py --nostatic)
    from django.conf.urls.static import static
    from chessclub.views import custom_serve

    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT, view=custom_serve
    )