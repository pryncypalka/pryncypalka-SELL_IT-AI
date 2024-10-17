from django.contrib import admin
from .models import Category, Subcategory, Item

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    list_display = ('subcategory_name', 'category')  # Fields to display in the subcategory list view

    extra = 1  # Number of empty forms for adding subcategories

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    model = Item
    extra = 1  # Number of empty forms for adding items

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)  # Fields to display in the category list view
    inlines = [SubcategoryInline]  # Inline form for adding subcategories to a category


