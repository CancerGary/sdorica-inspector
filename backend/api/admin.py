from django.contrib import admin

# Register your models here.
from backend.api.models import GameVersion,Imperium

admin.site.register(GameVersion)
admin.site.register(Imperium)