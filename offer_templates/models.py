from django.db import models
from products.models import Category
from django.utils import timezone
from django.conf import settings

class Template(models.Model):
    title = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(max_length=3000, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
