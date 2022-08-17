from django.contrib import admin

from .models import RatingStar, User, ChatDialog, ChatMessage, Rating


class RatingInline(admin.TabularInline):
    model = Rating


@admin.register(ChatDialog)
class ChatDialogAdmin(admin.ModelAdmin):
    inlines = [RatingInline]


admin.site.register(RatingStar)
admin.site.register(User)
admin.site.register(ChatMessage)
