document.addEventListener("DOMContentLoaded", () => {
    const wardrobeContainer = document.getElementById('wardrobe-items');
    const recommendationsContainer = document.getElementById('recommendation-items');
    const uploadForm = document.getElementById('upload-form');

    // Fetch wardrobe data
    async function fetchWardrobe() {
        try {
            const response = await fetch('/wardrobe_data');
            const data = await response.json();
            renderWardrobe(data);
        } catch (error) {
            console.error("Error fetching wardrobe:", error);
        }
    }

    // Render wardrobe items
    function renderWardrobe(items) {
        if (items.length === 0) {
            wardrobeContainer.innerHTML = "<p>No items yet. Start uploading!</p>";
            return;
        }

        wardrobeContainer.innerHTML = items.map(item => `
            <div class="wardrobe-item">
                <img src="/uploads/${item.filename}" alt="${item.category}" />
                <p>Category: ${item.category}</p>
                <p>${item.classification.most_likely_class}</p>
            </div>
        `).join('');
    }

    // Render recommendations
    function renderRecommendations(recommendations) {
        if (recommendations.length === 0) {
            recommendationsContainer.innerHTML = "<p>No recommendations available.</p>";
            return;
        }

        recommendationsContainer.innerHTML = recommendations.map(item => `
            <div class="recommendation-item">
                <img src="/uploads/${item.filename}" alt="${item.category}" />
                <p>Category: ${item.category}</p>
                <p>${item.classification.most_likely_class}</p>
            </div>
        `).join('');
    }

    // Handle upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent the default form submission
        const formData = new FormData(uploadForm);

        try {
            const response = await fetch('/upload_item', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                renderWardrobe([result.uploaded_item]); // Add the uploaded item to the wardrobe
                renderRecommendations(result.recommendations); // Display recommendations
            } else {
                alert("Error: " + result.error);
            }
        } catch (error) {
            console.error("Upload error:", error);
        }
    });

    fetchWardrobe(); // Initial fetch
});
