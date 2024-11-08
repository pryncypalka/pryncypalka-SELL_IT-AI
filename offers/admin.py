from django.contrib import admin
from .models import Offer, Photo, Category
from .widgets import CategorySelectWidget, DescriptionWidget
import openai
from django.urls import path
from django.http import JsonResponse  
from project import settings
openai.api_key = settings.OPENAI_API_KEY


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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-description/', self.generate_description, name='generate-description'),
        ]
        return custom_urls + urls
    
    def generate_description(self, request):
        try:
            title = request.GET.get('title', '')
            category = request.GET.get('category', '')
            
            prompt = f"""Napisz profesjonalny opis oferty sprzedaży dla produktu:
            Tytuł: {title}
            Kategoria: {category}
            
            Opis powinien być:
            - Szczegółowy ale zwięzły
            - Profesjonalny
            - Zawierać najważniejsze cechy produktu
            - Być napisany w języku polskim
            """
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            
            content = response.choices[0].message.content
            return JsonResponse({'status': 'success', 'content': content})
        except Exception as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})
        
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = DescriptionWidget()
        return super().formfield_for_dbfield(db_field, **kwargs)   
    
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
    list_display = ('category_name',)  


