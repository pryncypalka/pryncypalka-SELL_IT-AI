from django.contrib import admin
from .models import ChatData
# Register your models here.
@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_used')  
