from django.contrib import admin
from .models import Offer, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1 
    readonly_fields = ['image_tag']  

    @admin.display(description='Thumbnail')
    def image_tag(self, obj):
        return obj.image_tag() 

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  
    inlines = [PhotoInline] 