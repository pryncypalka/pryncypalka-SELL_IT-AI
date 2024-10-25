from django.contrib import admin
from .models import Category



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)  # Fields to display in the category list view


