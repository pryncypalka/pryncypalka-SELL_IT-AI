document.addEventListener('DOMContentLoaded', function() {
    // Inicjalizacja zmiennych
    const form = document.querySelector('form');
    const categorySelection = document.getElementById('categorySelection');
    const categoryIdInput = document.querySelector('[name="category_id"]');
    let selectedCategory = null;
    const eanInput = document.getElementById('eanSearch');
    const phraseInput = document.getElementById('phraseSearch');
    const searchEanBtn = document.getElementById('searchEanBtn');
    const searchPhraseBtn = document.getElementById('searchPhraseBtn');
    const productsList = document.getElementById('productsList');

    // Obsługa wyboru produktu z Allegro
    window.selectProduct = async function(product) {
        try {
            const response = await fetch('/api/allegro/products/select/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    productId: product.id
                })
            });
            
            if (response.ok) {
                // Wypełnij formularz danymi z produktu
                document.querySelector('[name="name"]').value = product.name;
                document.querySelector('[name="allegro_product_id"]').value = product.id;
                
                if (product.category?.id) {
                    categoryIdInput.value = product.category.id;
                    document.getElementById('selectedCategoryInfo').innerHTML = `
                        <strong>Wybrana kategoria:</strong> ${product.category.name}
                    `;
                }

                // Ustaw opis w CKEditor
                if (product.description) {
                    CKEDITOR.instances.description.setData(product.description);
                }

                // Ukryj wyniki wyszukiwania
                document.getElementById('searchResults').innerHTML = '';
            }
        } catch (error) {
            console.error('Error selecting product:', error);
            alert('Wystąpił błąd podczas wyboru produktu');
        }
    };

    // Obsługa wyboru kategorii - podobnie jak w offer_create.js
    async function loadCategories(parentId = null) {
        try {
            const response = await fetch(`/api/allegro/categories/${parentId || ''}`);
            const data = await response.json();
            renderCategories(data.categories, parentId);
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    function renderCategories(categories, parentId) {
        const container = parentId ? 
            document.getElementById(`subcategories-${parentId}`) : 
            categorySelection;

        const ul = document.createElement('ul');
        ul.className = 'list-group list-group-flush';

        categories.forEach(category => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `
                <div class="d-flex align-items-center">
                    ${!category.leaf ? `
                        <button type="button" class="btn btn-sm btn-link p-0 me-2 expand-category" 
                                data-id="${category.id}">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    ` : '<span class="me-4"></span>'}
                    <a href="#" class="select-category" data-id="${category.id}" 
                       data-name="${category.name}">${category.name}</a>
                </div>
                <div class="subcategories collapse" id="subcategories-${category.id}"></div>
            `;
            ul.appendChild(li);
        });

        if (!parentId) {
            container.innerHTML = '';
        }
        container.appendChild(ul);
    }

    // Event listeners
    document.addEventListener('click', async function(e) {
        if (e.target.closest('.expand-category')) {
            const btn = e.target.closest('.expand-category');
            const categoryId = btn.dataset.id;
            const icon = btn.querySelector('i');
            const container = document.querySelector(`#subcategories-${categoryId}`);
            
            if (!container.children.length) {
                await loadCategories(categoryId);
            }
            
            icon.classList.toggle('fa-chevron-right');
            icon.classList.toggle('fa-chevron-down');
            container.classList.toggle('show');
        }
        
        if (e.target.closest('.select-category')) {
            e.preventDefault();
            const link = e.target.closest('.select-category');
            categoryIdInput.value = link.dataset.id;
            document.getElementById('selectedCategoryInfo').innerHTML = `
                <strong>Wybrana kategoria:</strong> ${link.dataset.name}
                <button type="button" class="btn btn-sm btn-link clear-category">zmień</button>
            `;
        }

        if (e.target.closest('.clear-category')) {
            categoryIdInput.value = '';
            document.getElementById('selectedCategoryInfo').innerHTML = '';
            categorySelection.innerHTML = '';
            loadCategories();
        }
    });

    // Inicjalizacja
    if (!categoryIdInput.value) {
        loadCategories();
    }
});