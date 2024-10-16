from django.contrib import admin
from .models import Offer, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1  # liczba pustych formularzy do dodania zdjęć

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  # pola, które wyświetlają się na liście ofert
    inlines = [PhotoInline]  # dodanie zdjęć do formularza edycji oferty