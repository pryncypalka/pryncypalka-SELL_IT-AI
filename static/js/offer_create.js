document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const form = document.querySelector('form');
    const nameInput = document.querySelector('[name="name"]');
    const categoryMatches = document.getElementById('categoryMatches');
    const categorySelection = document.getElementById('categorySelection');
    const categoryIdInput = document.querySelector('[name="category_id"]');
    const parametersContainer = document.getElementById('parametersContainer');
    const imageInput = document.getElementById('images');
    const imagePreview = document.getElementById('imagePreview');

    let debounceTimer;

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
        try {
            const response = await fetch(`/api/allegro/matching-categories/?name=${encodeURIComponent(name)}`);
            const data = await response.json();
            renderCategoryMatches(data.matchingCategories || []);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    }

    function renderCategoryMatches(categories) {
        categoryMatches.innerHTML = categories.map(cat => `
            <div class="suggestion p-2 border-bottom">
                <a href="#" class="select-category" data-id="${cat.id}">
                    ${cat.name} 
                    ${cat.parent ? `<small class="text-muted">(${cat.parent.name})</small>` : ''}
                </a>
            </div>
        `).join('');
    }

    // Category Tree
    async function loadCategories(parentId = null, container = categorySelection) {
        try {
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
                        <a href="#" class="select-category" data-id="${cat.id}">${cat.name}</a>
                    </div>
                    <div class="subcategories collapse" id="subcategories-${cat.id}"></div>
                `;
                ul.appendChild(li);
            });

            if (!parentId) {
                container.innerHTML = '';
            }
            container.appendChild(ul);
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    // Category Selection Events
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
            categoryIdInput.value = categoryId;
            await loadParameters(categoryId);
        }
    });

    // Parameters
    async function loadParameters(categoryId) {
        try {
            const response = await fetch(`/api/allegro/categories/${categoryId}/parameters`);
            const data = await response.json();
            renderParameters(data.parameters);
        } catch (error) {
            console.error('Error loading parameters:', error);
        }
    }

    function renderParameters(parameters) {
        parametersContainer.innerHTML = parameters.map(param => `
            <div class="mb-3">
                <label class="form-label">
                    ${param.name}
                    ${param.required ? '<span class="text-danger">*</span>' : ''}
                </label>
                ${renderParameterInput(param)}
            </div>
        `).join('');
    }

    function renderParameterInput(param) {
        if (param.type === 'dictionary' && param.dictionary) {
            return `
                <select name="param_${param.id}" class="form-select" ${param.required ? 'required' : ''}>
                    <option value="">Select...</option>
                    ${param.dictionary.map(item => 
                        `<option value="${item.id}">${item.value}</option>`
                    ).join('')}
                </select>`;
        }
        
        if (param.type === 'range') {
            return `
                <div class="row">
                    <div class="col">
                        <input type="number" name="param_${param.id}_from" 
                               class="form-control" placeholder="From"
                               min="${param.restrictions?.min || ''}" 
                               max="${param.restrictions?.max || ''}"
                               ${param.required ? 'required' : ''}>
                    </div>
                    <div class="col">
                        <input type="number" name="param_${param.id}_to" 
                               class="form-control" placeholder="To"
                               min="${param.restrictions?.min || ''}" 
                               max="${param.restrictions?.max || ''}"
                               ${param.required ? 'required' : ''}>
                    </div>
                </div>`;
        }

        return `
            <input type="${param.type === 'integer' ? 'number' : 'text'}"
                   name="param_${param.id}"
                   class="form-control"
                   ${param.required ? 'required' : ''}>`;
    }

    // Initialize
    loadCategories();
});
