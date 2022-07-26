from django.contrib import admin
from .models import RatingStar, User, ChatDialog, ChatMessage, Rating


admin.site.register(RatingStar)
admin.site.register(User)
admin.site.register(ChatDialog)
admin.site.register(ChatMessage)
admin.site.register(Rating)
