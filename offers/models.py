from django.db import models
from django.utils import timezone
from django.conf import settings
from products.models import Item
class Offer(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=255, null=False)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    description = models.TextField(max_length=3000, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Photos related to the offer
    # The reverse relationship will be defined in the Photo model

    def __str__(self):
        return self.title

class Photo(models.Model):
    photo_path = models.CharField(max_length=255, null=False)

    offer = models.ForeignKey('Offer', on_delete=models.CASCADE)

    def __str__(self):
        return self.photo_path