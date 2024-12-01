document.addEventListener('DOMContentLoaded', function() {
    const eanInput = document.getElementById('eanSearch');
    const phraseInput = document.getElementById('phraseSearch');
    const searchEanBtn = document.getElementById('searchEanBtn');
    const searchPhraseBtn = document.getElementById('searchPhraseBtn');
    const productsList = document.getElementById('productsList');
    const productTemplate = document.getElementById('productCardTemplate');

    // Wyszukiwanie po EAN
    searchEanBtn.addEventListener('click', () => {
        const ean = eanInput.value.trim();
        if (ean) {
            searchProducts('ean', ean);
        }
    });

    // Wyszukiwanie po frazie
    searchPhraseBtn.addEventListener('click', () => {
        const phrase = phraseInput.value.trim();
        if (phrase) {
            searchProducts('phrase', phrase);
        }
    });

    async function searchProducts(type, value) {
        try {
            const params = new URLSearchParams();
            if (type === 'ean') {
                params.append('mode', 'GTIN');
                params.append('phrase', value);
            } else {
                params.append('phrase', value);
            }

            const response = await fetch(`/api/allegro/products/search/?${params.toString()}`);
            const data = await response.json();
            
            displayResults(data.products || []);
        } catch (error) {
            console.error('Search error:', error);
            // Dodaj obsługę błędów
        }
    }

    function displayResults(products) {
        productsList.innerHTML = '';
        
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'col-md-4 mb-4';
            card.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h6 class="card-title mb-0">${product.name}</h6>
                            ${product.images.length > 0 ? 
                                `<img src="${product.images[0]}" class="img-thumbnail" 
                                 style="width: 60px; height: 60px; object-fit: cover;">` : 
                                `<div class="bg-light rounded" style="width: 60px; height: 60px; 
                                 display: flex; align-items: center; justify-content: center;">
                                    <i class="fas fa-image text-muted"></i>
                                 </div>`
                            }
                        </div>
                        
                        <div class="small">
                            <p class="mb-1">
                                <strong>EAN:</strong> 
                                <span>${product.ean || 'Brak'}</span>
                            </p>
                            <p class="mb-1">
                                <strong>Kategoria:</strong> 
                                <span>${product.category?.name || 'Brak'}</span>
                            </p>
                            <p class="mb-1">
                                <strong>Producent:</strong> 
                                <span>${product.producer || 'Brak'}</span>
                            </p>
                            
                            ${product.parameters.length > 0 ? `
                                <div class="mt-2">
                                    <strong>Parametry:</strong>
                                    <ul class="list-unstyled ps-3 mb-0">
                                        ${product.parameters.slice(0, 3).map(param => `
                                            <li>${param.name}: ${param.values?.join(', ') || 'Brak'}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-primary btn-sm w-100 select-product" 
                                data-product-id="${product.id}">
                            Wybierz ten produkt
                        </button>
                    </div>
                </div>
            `;
            
            const selectBtn = card.querySelector('.select-product');
            selectBtn.addEventListener('click', () => selectProduct(product));
            
            productsList.appendChild(card);
        });
        
        if (products.length === 0) {
            productsList.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        Nie znaleziono produktów. Spróbuj zmienić kryteria wyszukiwania lub 
                        <a href="/allegro/offers/create/" class="alert-link">
                            utwórz nowy produkt
                        </a>.
                    </div>
                </div>`;
        }
    }

    async function selectProduct(product) {
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
                // Przekieruj do formularza tworzenia oferty z wybranym produktem
                window.location.href = `/allegro/offers/create/?product_id=${product.id}`;
            }
        } catch (error) {
            console.error('Error selecting product:', error);
        }
    }
    
    // Obsługa Enter w polach wyszukiwania
    eanInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchEanBtn.click();
    });
    
    phraseInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchPhraseBtn.click();
    });
});