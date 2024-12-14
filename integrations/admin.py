from django.contrib import admin
from .models import AllegroToken
from simple_history import register
from django.contrib.auth.models import User

register(User)

admin.site.register(AllegroToken)