from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from backend.api.models import DiscordInvite


class DiscordInviteAdmin(admin.ModelAdmin):
    list_display = ['id', 'discord_id']
    search_fields = ['discord_id']


class NewUserAdmin(UserAdmin):
    list_display = ['username', 'discord_id', 'last_login']
    list_select_related = ['profile']
    search_fields = ['username', 'profile__discord_id']

    def discord_id(self, obj):
        return obj.profile.discord_id


admin.site.register(DiscordInvite, DiscordInviteAdmin)
admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
