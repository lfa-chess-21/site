from django.contrib import admin

# Register your models here.
from games.models import ChessGame

admin.site.register(ChessGame)
