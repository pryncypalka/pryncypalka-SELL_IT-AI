from django.contrib import admin
from .models import Offer, Photo, Category
from .forms import CategorySelectWidget
        
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
    fields = ['title', 'category', 'description', 'price']
    raw_id_fields = ['category']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs['widget'] = CategorySelectWidget()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change or obj.user is None:
            obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Offer, OfferAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)  # Fields to display in the category list view


