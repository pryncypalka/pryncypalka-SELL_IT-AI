from django.contrib import admin
from .models import Template

@admin.register(Template)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')  