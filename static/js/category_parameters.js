// const categorySelect = document.querySelector('[name="category_id"]');
// const parametersContainer = document.getElementById('parametersContainer');

// async function loadSubcategories(parentId = null) {
//     const url = `/api/allegro/categories/${parentId || ''}`;
//     const response = await fetch(url);
//     const categories = await response.json();
    
//     return categories.categories || [];
// }

// async function loadParameters(categoryId) {
//     const url = `/api/allegro/categories/${categoryId}/parameters`;
//     const response = await fetch(url);
//     const data = await response.json();
    
//     renderParameters(data.parameters);
// }

// function renderParameters(parameters) {
//     parametersContainer.innerHTML = parameters.map(param => `
//         <div class="mb-3">
//             <label class="form-label">
//                 ${param.name}
//                 ${param.required ? '<span class="text-danger">*</span>' : ''}
//             </label>
//             ${renderParameterInput(param)}
//         </div>
//     `).join('');
// }

// function renderParameterInput(param) {
//     if (param.type === 'dictionary' && param.dictionary) {
//         return `
//             <select name="param_${param.id}" class="form-select" ${param.required ? 'required' : ''}>
//                 <option value="">Select...</option>
//                 ${param.dictionary.map(item => 
//                     `<option value="${item.id}">${item.value}</option>`
//                 ).join('')}
//             </select>`;
//     }
    
//     if (param.type === 'range') {
//         return `
//             <div class="row">
//                 <div class="col">
//                     <input type="number" name="param_${param.id}_from" 
//                            class="form-control" placeholder="From"
//                            min="${param.restrictions?.min || ''}" 
//                            max="${param.restrictions?.max || ''}"
//                            ${param.required ? 'required' : ''}>
//                 </div>
//                 <div class="col">
//                     <input type="number" name="param_${param.id}_to" 
//                            class="form-control" placeholder="To"
//                            min="${param.restrictions?.min || ''}" 
//                            max="${param.restrictions?.max || ''}"
//                            ${param.required ? 'required' : ''}>
//                 </div>
//             </div>`;
//     }

//     return `
//         <input type="${param.type === 'integer' ? 'number' : 'text'}"
//                name="param_${param.id}"
//                class="form-control"
//                ${param.required ? 'required' : ''}>`;
// }

// categorySelect.addEventListener('change', (e) => {
//     const categoryId = e.target.value;
//     if (categoryId) {
//         loadParameters(categoryId);
//     }
// });

// // Initialize root categories
// loadSubcategories().then(categories => {
//     categorySelect.innerHTML = `
//         <option value="">Select category...</option>
//         ${categories.map(cat => 
//             `<option value="${cat.id}">${cat.name}</option>`
//         ).join('')}`;
// });