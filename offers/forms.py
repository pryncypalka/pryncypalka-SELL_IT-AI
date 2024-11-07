from django import forms
from django.utils.html import escapejs
from django.core.serializers import serialize
from .models import Category
from django import forms
from .models import Category

class CategorySelectWidget(forms.Select):
    template_name = 'offers/category_select.html'  
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        top_level_categories = Category.objects.filter(parent__isnull=True)
        categories_data = [
            {
                'id': category.id,
                'name': category.category_name,
                'image': category.image.url if category.image else None,
                'subcategories': category.get_subcategories()
            }
            for category in top_level_categories
        ]
        
        context['categories_data'] = categories_data  
        context['name'] = name
        context['value'] = value
        return context

    

       