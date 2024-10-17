import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from products.models import Category, Subcategory, Item


def populate_data():
    for i in range(1, 6):
        category_name = f"Category {i}"
        category = Category.objects.create(category_name=category_name)
        print(f"Created {category}")

        for j in range(1, 3):
            subcategory_name = f"Subcategory {j} "
            subcategory = Subcategory.objects.create(
                subcategory_name=subcategory_name,
                category=category
            )
            print(f"Created {subcategory}")

            for k in range(1, 3):
                item_name = f"Item {i+k+j}"
                item = Item.objects.create(
                    item_name=item_name,
                    subcategory=subcategory
                )
                print(f"Created {item}")

if __name__ == "__main__":
    populate_data()