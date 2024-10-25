import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from products.models import Category

def populate_data():
    # Definicja drzewa kategorii
    categories = {
        "Motoryzacja": [
            "Samochody",
            "Motocykle i skutery",
            "Części i akcesoria"
        ],
        "Elektronika": [
            "Telefony komórkowe",
            "Komputery",
            "RTV i AGD"
        ],
        "Nieruchomości": [
            "Mieszkania",
            "Domy",
            "Działki"
        ],
        "Moda": [
            "Odzież damska",
            "Odzież męska",
            "Obuwie"
        ],
        "Dla dzieci": [
            "Zabawki",
            "Ubranka",
            "Wózki"
        ]
    }

    # Tworzenie kategorii głównych i ich podkategorii
    for category_name, subcategory_names in categories.items():
        # Tworzenie kategorii głównej
        main_category = Category.objects.create(category_name=category_name)
        print(f"Created Main Category: {main_category}")

        # Tworzenie podkategorii dla głównej kategorii
        for subcategory_name in subcategory_names:
            subcategory = Category.objects.create(
                category_name=subcategory_name,
                parent=main_category  # Ustawienie głównej kategorii jako rodzica
            )
            print(f"  Created Subcategory: {subcategory}")

if __name__ == "__main__":
    populate_data()
