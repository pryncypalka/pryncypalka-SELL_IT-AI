from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Subcategory(models.Model):
    subcategory_name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subcategory_name} ({self.category.category_name})"

    class Meta:
        verbose_name_plural = "Subcategories"


class Item(models.Model):
    item_name = models.CharField(max_length=255, null=False)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # Pole do przesyłania zdjęć

    def __str__(self):
        return self.item_name

    class Meta:
        verbose_name_plural = "Items"
