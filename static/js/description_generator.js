document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-description');
    const descriptionField = document.getElementById('id_description');
    const titleField = document.getElementById('id_title');
    const categoryField = document.getElementById('category-name-display');

    if (generateBtn && descriptionField) {
        generateBtn.addEventListener('click', async function() {
            try {
                console.log("Starting description generation...");  // Log: Początek generowania opisu
                generateBtn.disabled = true;

                const title = titleField.value;
                const categoryName = categoryField.value;

                console.log("Title:", title);  // Log: Wyświetl tytuł oferty
                console.log("Category name :", categoryName);  // Log: Wyświetl ID kategorii

               

                const response = await fetch(`/offers/offer/generate-description/?title=${encodeURIComponent(title)}&category=${encodeURIComponent(categoryName)}`);
                
                if (!response.ok) {
                    const errorText = await response.text(); 
                    console.error("Error response from server:", errorText);
                    throw new Error("Failed to fetch description from server");
                }
                
                const data = await response.json();
                console.log("Data from server:", data);  // Log: Dane z serwera

                if (data.status === 'success') {
                    descriptionField.value = data.content;
                
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error("Error:", error);  
              
            } finally {
                generateBtn.disabled = false;
            }
        });
    }
});
