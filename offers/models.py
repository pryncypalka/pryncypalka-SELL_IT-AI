from django.db import models
from django.utils import timezone
from django.conf import settings
from products.models import Item
import os
import uuid
from django.utils.html import mark_safe

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # Dodaje podkatalog z ID oferty
    return os.path.join(f'offers/{instance.offer.id}', filename)


class Offer(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=255, null=False)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    description = models.TextField(max_length=3000, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Photo(models.Model):
    photo = models.ImageField(upload_to=get_file_path, null=True, blank=True)  


    offer = models.ForeignKey('Offer', on_delete=models.CASCADE)

    def __str__(self):
        return self.offer.title
    
    def image_tag(self):
        if self.photo:
            return mark_safe(f'<img src="{self.photo.url}" width="100" height="100" />')
        return "No Image"