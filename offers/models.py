# from django.db import models
# from django.utils import timezone
# from django.conf import settings
# from django.utils.html import mark_safe

# import os
# import uuid


# class Category(models.Model):
#     category_name = models.CharField(max_length=255, null=False)
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
#     image = models.ImageField(upload_to='images/', null=True, blank=True)  

#     def __str__(self):
#         if self.parent:
#             return f"{self.category_name} (Subcategory of {self.parent.category_name})"
#         return self.category_name
    
#     def get_subcategories(self):
#         """
#         Recursive method to retrieve all subcategories.
#         """
#         subcategories = []
#         for subcategory in self.subcategories.all():
#             subcategories.append({
#                 'id': subcategory.id,
#                 'name': subcategory.category_name,
#                 'image': subcategory.image.url if subcategory.image else None,
#                 'subcategories': subcategory.get_subcategories()
#             })
#         return subcategories

#     class Meta:
#         verbose_name_plural = "Categories"




# def get_file_path(instance, filename):
#     ext = filename.split('.')[-1]
#     filename = f"{uuid.uuid4()}.{ext}"
#     # Dodaje podkatalog z ID oferty
#     return os.path.join(f'offers/{instance.offer.id}', filename)


# class Offer(models.Model):
#     price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

#     created_at = models.DateTimeField(default=timezone.now)

#     title = models.CharField(max_length=255, null=False)

#     category = models.ForeignKey(Category, on_delete=models.CASCADE)

#     description = models.TextField(max_length=3000, null=True)

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.title

# class Photo(models.Model):
#     photo = models.ImageField(upload_to=get_file_path, null=True, blank=True)  


#     offer = models.ForeignKey('Offer', on_delete=models.CASCADE)

#     def __str__(self):
#         return self.offer.title
    
#     def image_tag(self):
#         if self.photo:
#             return mark_safe(
#                 f'<img src="{self.photo.url}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />'
#             )
#         return "No Image"