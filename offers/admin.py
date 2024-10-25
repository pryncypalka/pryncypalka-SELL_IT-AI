from django.contrib import admin
from .models import Offer, Photo


    
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1 
    readonly_fields = ['image_tag']
    
    @admin.display(description='Preview')
    def image_tag(self, obj):
        if obj:
            return obj.image_tag()
        return "No Image"



class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  
    inlines = [PhotoInline]

    # Określ kolejność pól w formularzu
    fields = ['title','category', 'description', 'price']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.user = request.user
        super().save_model(request, obj, form, change)

    
admin.site.register(Offer, OfferAdmin)
