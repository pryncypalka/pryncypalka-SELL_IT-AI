from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='images/', null=True, blank=True)  

    def __str__(self):
        if self.parent:
            return f"{self.category_name} (Subcategory of {self.parent.category_name})"
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"

