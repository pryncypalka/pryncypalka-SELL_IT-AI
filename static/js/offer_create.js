document.addEventListener('DOMContentLoaded', function() {
    // Podstawowe elementy DOM
    const form = document.querySelector('form');
    const nameInput = document.querySelector('[name="name"]');
    const categoryMatches = document.getElementById('categoryMatches');
    const categorySelection = document.getElementById('categorySelection');
    const categoryIdInput = document.querySelector('[name="category_id"]');
    const parametersContainer = document.getElementById('parametersContainer');
    const imageInput = document.getElementById('images');
    const imagePreview = document.getElementById('imagePreview');
    const uploadedImagesContainer = document.getElementById('uploadedImages');
    const productId = document.getElementById('productId')?.value;

    // Inicjalizacja zmiennych
    let debounceTimer;
    let uploadedImages = [];

    // Inicjalizacja kontenera kategorii
    const selectedCategoryContainer = document.createElement('div');
    selectedCategoryContainer.className = 'selected-category mt-2 p-2 border rounded';
    categorySelection.parentNode.insertBefore(selectedCategoryContainer, categorySelection);


    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Sprawdź czy są zdjęcia
        if (!uploadedImages.length) {
            alert('Dodaj przynajmniej jedno zdjęcie.');
            return;
        }

        const formData = new FormData(this);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage(result.message || 'Pomyślnie utworzono ofertę', 'success');
            } else {
                showMessage(result.message || 'Wystąpił błąd podczas tworzenia oferty', 'error');
            }
        } catch (error) {
            showMessage('Wystąpił błąd podczas przetwarzania formularza', 'error');
            console.error('Form submission error:', error);
        }
    });

    // Jeśli mamy initial_data, wypełnij formularz
    if (initialData) {
        console.log("Processing initial data:", initialData); // Debug
        
        // Wypełnij nazwę
        if (nameInput && initialData.name) {
            console.log("Setting name:", initialData.name);
            nameInput.value = initialData.name;
            if (productId) {
                nameInput.readOnly = true;
            }
        }

        // Wypełnij kategorię
        if (initialData.category) {
            console.log("Setting category:", initialData.category);
            const categoryIdInput = document.querySelector('[name="category_id"]');
            if (categoryIdInput) {
                categoryIdInput.value = initialData.category.id;
            }
            
            const selectedCategoryContainer = document.querySelector('.selected-category');
            if (selectedCategoryContainer) {
                selectedCategoryContainer.innerHTML = `
                    <strong>Kategoria:</strong> ${initialData.category.name}
                    ${!productId ? '<button type="button" class="btn btn-sm btn-link clear-category">zmień</button>' : ''}
                `;
            }
        }

        // Wypełnij parametry
        if (initialData.parameters) {
            console.log("Setting parameters:", initialData.parameters);
            renderParameters(initialData.parameters);
        }

        // Wstępnie załaduj zdjęcia
        if (initialData.images && initialData.images.length > 0) {
            console.log("Setting images:", initialData.images);
            initialData.images.forEach(imageUrl => {
                uploadedImages.push(imageUrl);
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'images[]';
                input.value = imageUrl;
                uploadedImagesContainer.appendChild(input);

                const previewDiv = document.createElement('div');
                previewDiv.className = 'col-md-3 mb-2';
                previewDiv.innerHTML = `
                    <div class="card h-100">
                        <img src="${imageUrl}" class="card-img-top" alt="Product image" 
                             style="height: 150px; object-fit: cover;">
                        ${!productId ? `
                            <div class="card-body p-2">
                                <button type="button" class="btn btn-sm btn-danger w-100">Usuń</button>
                            </div>
                        ` : ''}
                    </div>
                `;
                imagePreview.appendChild(previewDiv);
            });
        }
    }

    // Jeśli mamy wybrany produkt, ukryj/zablokuj niektóre pola
    if (productId) {
        // Ukryj sekcję wyboru kategorii
        document.querySelector('.category-selection')?.classList.add('d-none');
        
        // Zablokuj edycję parametrów
        const inputs = parametersContainer.querySelectorAll('input, select');
        inputs.forEach(input => input.disabled = true);
        
        // Ukryj przycisk dodawania zdjęć
        document.querySelector('#images')?.closest('.mb-3')?.classList.add('d-none');
    }


    imageInput.addEventListener('change', async function(e) {
        const files = Array.from(e.target.files);
        for (const file of files) {
            await handleImageUpload(file);
        }
    });

    async function handleImageUpload(file) {
        // Create preview
        const previewDiv = document.createElement('div');
        previewDiv.className = 'col-md-3 mb-2';
        previewDiv.innerHTML = `
            <div class="card h-100">
                <div class="position-relative">
                    <img src="${URL.createObjectURL(file)}" class="card-img-top" 
                         alt="Preview" style="height: 150px; object-fit: cover;">
                    <div class="position-absolute top-0 start-0 w-100 h-100 d-flex 
                         justify-content-center align-items-center upload-overlay" 
                         style="background: rgba(0,0,0,0.5);">
                        <div class="spinner-border text-light" role="status"></div>
                    </div>
                </div>
                <div class="card-body p-2">
                    <button type="button" class="btn btn-sm btn-danger w-100" disabled>Usuń</button>
                </div>
            </div>
        `;
        imagePreview.appendChild(previewDiv);

        // Upload to server
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/api/allegro/upload-image/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            });

            if (!response.ok) throw new Error('Upload failed');
            
            const result = await response.json();
            uploadedImages.push(result.url);
            
            // Update UI after successful upload
            const overlay = previewDiv.querySelector('.upload-overlay');
            const deleteBtn = previewDiv.querySelector('.btn-danger');
            overlay.remove();
            deleteBtn.disabled = false;
            
            updateHiddenInputs();
        } catch (error) {
            console.error('Upload error:', error);
            previewDiv.remove();
            alert('Błąd podczas przesyłania zdjęcia');
        }
    }

    // Delete image handler
    imagePreview.addEventListener('click', function(e) {
        if (e.target.matches('.btn-danger')) {
            const imageContainer = e.target.closest('.col-md-3');
            const index = Array.from(imagePreview.children).indexOf(imageContainer);
            uploadedImages.splice(index, 1);
            imageContainer.remove();
            updateHiddenInputs();
        }
    });

    function updateHiddenInputs() {
        uploadedImagesContainer.innerHTML = '';
        uploadedImages.forEach(url => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'images[]';
            input.value = url;
            uploadedImagesContainer.appendChild(input);
        });
    }

 
    // Category Search
    nameInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            if (this.value.length > 2) {
                try {
                    await searchCategories(this.value);
                } catch (error) {
                    console.error('Error fetching categories:', error);
                }
            } else {
                categoryMatches.innerHTML = '';
            }
        }, 300);
    });

    async function searchCategories(name) {
        const response = await fetch(`/api/allegro/matching-categories/?name=${encodeURIComponent(name)}`);
        const data = await response.json();
        renderCategoryMatches(data.matchingCategories || []);
    }

    function renderCategoryMatches(categories) {
    categoryMatches.innerHTML = categories.length > 0 ? 
        `<div class="mb-2"><strong>Proponowane kategorie:</strong></div>` +
        categories.map(cat => `
            <div class="suggestion p-2 border-bottom">
                <a href="#" class="select-category" data-id="${cat.id}" data-name="${cat.name}">
                    ${cat.name} 
                    ${cat.parent ? `<small class="text-muted">(${cat.parent.name})</small>` : ''}
                </a>
            </div>
        `).join('') : '';
}

    // Category Tree Navigation
    async function loadCategories(parentId = null, container = categorySelection) {
        const response = await fetch(`/api/allegro/categories/${parentId || ''}`);
        const data = await response.json();
        
        const ul = document.createElement('ul');
        ul.className = 'list-group list-group-flush';
        
        data.categories.forEach(cat => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `
                <div class="d-flex align-items-center">
                    ${!cat.leaf ? `
                        <button type="button" class="btn btn-sm btn-link p-0 me-2 expand-category" data-id="${cat.id}">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    ` : '<span class="me-4"></span>'}
                    <a href="#" class="select-category" data-id="${cat.id}" data-name="${cat.name}">${cat.name}</a>
                </div>
                <div class="subcategories collapse" id="subcategories-${cat.id}"></div>
            `;
            ul.appendChild(li);
        });

        if (!parentId) {
            container.innerHTML = '';
        }
        container.appendChild(ul);
    }

    document.addEventListener('click', async function(e) {
        if (e.target.closest('.expand-category')) {
            const btn = e.target.closest('.expand-category');
            const categoryId = btn.dataset.id;
            const icon = btn.querySelector('i');
            const container = document.querySelector(`#subcategories-${categoryId}`);
            
            if (!container.children.length) {
                await loadCategories(categoryId, container);
            }
            
            icon.classList.toggle('fa-chevron-right');
            icon.classList.toggle('fa-chevron-down');
            container.classList.toggle('show');
        }
        
        if (e.target.closest('.select-category')) {
            e.preventDefault();
            const link = e.target.closest('.select-category');
            const categoryId = link.dataset.id;
            const categoryName = link.dataset.name;
            categoryIdInput.value = categoryId;
            selectedCategoryContainer.innerHTML = `
                <strong>Wybrana kategoria:</strong> ${categoryName}
                <button type="button" class="btn btn-sm btn-link clear-category">zmień</button>
            `;
            await loadParameters(categoryId);
        }

        if (e.target.closest('.clear-category')) {
            categoryIdInput.value = '';
            selectedCategoryContainer.innerHTML = '';
            parametersContainer.innerHTML = '';
        }
    });

    // Parameters handling
    async function loadParameters(categoryId) {
        const response = await fetch(`/api/allegro/categories/${categoryId}/parameters`);
        const data = await response.json();
        renderParameters(data.parameters);
    }

    function renderParameters(parameters) {
        console.log("Rendering parameters:", parameters);  // Debug log
        
        parametersContainer.innerHTML = parameters.map(param => {
            // Debug log dla każdego parametru
            console.log(`Processing parameter:`, param);
            
            let value = '';
            if (param.values && param.values.length > 0) {
                value = param.values[0];
            } else if (param.valuesIds && param.valuesIds.length > 0) {
                value = param.valuesIds[0];
            }
            console.log(`Parameter ${param.name} value:`, value);
    
            return `
                <div class="mb-3">
                    <label class="form-label">
                        ${param.name}
                        ${param.required ? '<span class="text-danger">*</span>' : ''}
                    </label>
                    ${createParameterInput(param)}
                </div>
            `;
        }).join('');
    }

    function createParameterInput(param) {
        // Debug log
        console.log('Creating input for parameter:', param);
        
        // Określenie wartości parametru
        let value = '';
        if (param.valuesIds && param.valuesIds.length > 0) {
            // Dla parametrów z valuesIds
            value = param.valuesIds[0];  // Przykład: "207786_233866"
        } else if (param.values && param.values.length > 0) {
            // Dla parametrów ze zwykłymi wartościami
            value = param.values[0];      // Przykład: "Lito"
        }
        
        // Tworzymy input w zależności od typu parametru
        if (param.type === 'dictionary' || param.valuesIds) {  // Jeśli parametr ma valuesIds, to traktujemy go jako słownikowy
            return `
                <select name="param_${param.id}" class="form-select" ${param.required ? 'required' : ''}>
                    <option value="">Wybierz...</option>
                    ${param.dictionary ? param.dictionary.map(item => 
                        `<option value="${item.id}" ${item.id === value ? 'selected' : ''}>
                            ${item.value}
                        </option>`
                    ).join('') : 
                    `<option value="${value}" selected>
                        ${param.valuesLabels ? param.valuesLabels[0] : value}
                    </option>`}
                </select>`;
        } else if (param.type === 'range') {
            return `
                <div class="row">
                    <div class="col">
                        <input type="number" 
                               name="param_${param.id}" 
                               class="form-control" 
                               value="${value}"
                               ${param.required ? 'required' : ''}>
                    </div>
                </div>`;
        }
    
        // Dla zwykłych pól tekstowych/liczbowych
        const inputType = param.type === 'integer' || param.unit === 'szt.' ? 'number' : 'text';
        return `
            <input type="${inputType}"
                   name="param_${param.id}"
                   class="form-control"
                   value="${value}"
                   ${param.unit ? `data-unit="${param.unit}"` : ''}
                   ${param.required ? 'required' : ''}>`;
    }

   
    // Message display helper
    function showMessage(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${alertClass} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Remove any existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
        
        // Insert at the top of the form
        form.insertAdjacentElement('afterbegin', messageDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            messageDiv.classList.remove('show');
            setTimeout(() => messageDiv.remove(), 150);
        }, 5000);
    }


    // Initialize default categories
    loadCategories();
});