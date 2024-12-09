# from django import forms
# from .models import Category
# from django import forms
# from .models import Category


# class CategorySelectWidget(forms.Select):
#     template_name = 'offers/category_select.html'  
    
#     def get_context(self, name, value, attrs):
#         context = super().get_context(name, value, attrs)
        
#         top_level_categories = Category.objects.filter(parent__isnull=True)
#         categories_data = [
#             {
#                 'id': category.id,
#                 'name': category.category_name,
#                 'image': category.image.url if category.image else None,
#                 'subcategories': category.get_subcategories()
#             }
#             for category in top_level_categories
#         ]
#         try:
#             category = Category.objects.get(id=value)
#             category_name = category.category_name
#         except Category.DoesNotExist:
#             category_name = "Select category"
        
#         context['categories_data'] = categories_data  
#         context['name'] = name
#         context['value'] = value
#         context['selected_category'] = category_name

#         return context


# class DescriptionWidget(forms.Textarea):
#     template_name = 'offers/description_widget.html'

#     def render(self, name, value, attrs=None, renderer=None):
#         if attrs is None:
#             attrs = {}
#         attrs['id'] = 'id_description'
        
#         textarea_html = super().render(name, value, attrs, renderer)
        
     
#         return textarea_html

#     class Media:
#         js = ('js/description_generator.js',)

       