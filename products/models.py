from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='images/', null=True, blank=True)  

    def __str__(self):
        if self.parent:
            return f"{self.category_name} (Subcategory of {self.parent.category_name})"
        return self.category_name
    
    def get_subcategories(self):
        """
        Recursive method to retrieve all subcategories.
        """
        subcategories = []
        for subcategory in self.subcategories.all():
            subcategories.append({
                'id': subcategory.id,
                'name': subcategory.category_name,
                'image': subcategory.image.url if subcategory.image else None,
                'subcategories': subcategory.get_subcategories()
            })
        return subcategories

    class Meta:
        verbose_name_plural = "Categories"

