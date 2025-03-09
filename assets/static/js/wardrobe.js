document.addEventListener("DOMContentLoaded", () => {
    const wardrobeContainer = document.getElementById("wardrobe-items");
    const uploadForm = document.getElementById("upload-form");
    const weatherContainer = document.getElementById("weather-container");

    // Add modal HTML to the page
    document.body.insertAdjacentHTML('beforeend', `
        <div id="recommendations-modal" class="modal">
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <h2>Recommended Matches</h2>
                <div id="modal-recommendations"></div>
            </div>
        </div>
    `);

    const modal = document.getElementById("recommendations-modal");
    const modalContent = document.getElementById("modal-recommendations");
    const closeBtn = document.querySelector(".close-modal");

    // Close modal when clicking the X button
    closeBtn.onclick = () => modal.style.display = "none";

    // Close modal when clicking outside
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    let currentWardrobeData = {};

    // Fetch wardrobe data
    async function fetchWardrobe() {
        try {
            const response = await fetch("/wardrobe_data");
            const data = await response.json();

            if (response.ok) {
                currentWardrobeData = data;
                renderWardrobe(data);
            } else {
                wardrobeContainer.innerHTML = `<p>Error: ${data.error}</p>`;
            }
        } catch (error) {
            console.error("Error fetching wardrobe:", error);
            wardrobeContainer.innerHTML = "<p>Error loading wardrobe items.</p>";
        }
    }

    // Render wardrobe items grouped by category
    function renderWardrobe(items) {
        if (!items || Object.keys(items).length === 0) {
            wardrobeContainer.innerHTML = "<p>No items found. Start uploading!</p>";
            return;
        }

        wardrobeContainer.innerHTML = Object.keys(items)
            .map((category) => {
                const categoryItems = items[category];
                return `
                <div class="category-group">
                    <h3>${category}</h3>
                    <div class="category-items">
                        ${categoryItems
                            .map(
                                (item) => 
                                `<div class="wardrobe-item" data-category="${category}" data-id="${item._id}">
                                    <img src="${item.image_path}" alt="Wardrobe Item" />
                                    <p>Top Prediction: ${item.classification.label || "Unknown"}</p>
                                    <p>Category: ${item.classification.category || "Unknown"}</p>
                                </div>`
                            )
                            .join("")}
                    </div>
                </div>`;
            })
            .join("");

        // Add click event listeners to wardrobe items
        document.querySelectorAll('.wardrobe-item').forEach(item => {
            item.addEventListener('click', selectWardrobeItem);
        });
    }

    // Select a wardrobe item and find recommendations
    function selectWardrobeItem(event) {
        // Remove previous selections
        document.querySelectorAll('.wardrobe-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Mark current item as selected
        event.currentTarget.classList.add('selected');

        // Get selected item details
        const selectedCategory = event.currentTarget.getAttribute('data-category');
        const selectedItemId = event.currentTarget.getAttribute('data-id');

        // Find and display recommendations in modal
        findRecommendations(selectedCategory, selectedItemId);
    }

    // Find recommendations based on selected item
    function findRecommendations(selectedCategory, selectedItemId) {
        const recommendationMap = {
            'Topwear': {
                'Blouse': ['Jeans', 'Skirt', 'Chinos', 'Leggings'],
                'Button-Down': ['Jeans', 'Chinos', 'Blazer'],
                'Flannel': ['Jeans', 'Sweatpants', 'Shorts'],
                'Halter': ['Shorts', 'Skirt', 'Jeans'],
                'Henley': ['Jeans', 'Joggers', 'Sweatpants'],
                'Jersey': ['Joggers', 'Shorts'],
                'Sweater': ['Jeans', 'Leggings', 'Skirt'],
                'Tank': ['Shorts', 'Skirt', 'Jeans'],
                'Tee': ['Jeans', 'Shorts', 'Skirt'],
                'Top': ['Jeans', 'Shorts', 'Leggings'],
                'Turtleneck': ['Skirt', 'Chinos', 'Jeans'],
            },
            'Bottomwear': {
                'Capris': ['Blouse', 'Tank', 'Tee'],
                'Chinos': ['Button-Down', 'Blazer', 'Sweater'],
                'Culottes': ['Blouse', 'Tank', 'Tee'],
                'Cutoffs': ['Tank', 'Tee', 'Flannel'],
                'Jeans': ['Tee', 'Sweater', 'Blouse', 'Jacket'],
                'Jeggings': ['Sweater', 'Turtleneck', 'Flannel'],
                'Joggers': ['Hoodie', 'Tee', 'Jersey'],
                'Leggings': ['Sweater', 'Tunic', 'Blouse'],
                'Shorts': ['Tank', 'Tee', 'Flannel'],
                'Skirt': ['Blouse', 'Sweater', 'Turtleneck'],
                'Sweatpants': ['Hoodie', 'Henley', 'Tee'],
                'Sweatshorts': ['Tank', 'Tee'],
                'Trunks': ['Tank', 'Tee'],
            },
            'Dresses': {
                'Dress': ['Blazer', 'Cardigan', 'Coat'],
                'Caftan': ['Leggings'],
                'Jumpsuit': ['Blazer', 'Cardigan'],
                'Kaftan': ['Leggings'],
                'Onesie': ['Cardigan', 'Jacket'],
                'Romper': ['Cardigan', 'Jacket'],
                'Sarong': ['Tank', 'Bikini Top'],
            },
            'Outerwear': {
                'Anorak': ['Tee', 'Jeans', 'Sweatpants'],
                'Blazer': ['Blouse', 'Button-Down', 'Chinos', 'Jeans'],
                'Bomber': ['Tee', 'Jeans', 'Sweatpants'],
                'Cardigan': ['Turtleneck', 'Tank', 'Jeans', 'Skirt'],
                'Coat': ['Sweater', 'Jeans', 'Dress'],
                'Hoodie': ['Tee', 'Joggers', 'Sweatpants','Tank'],
                'Jacket': ['Tee', 'Jeans', 'Dress'],
                'Kimono': ['Tank', 'Jeans', 'Shorts'],
                'Parka': ['Sweater', 'Jeans', 'Sweatpants'],
                'Peacoat': ['Turtleneck', 'Jeans', 'Chinos'],
                'Poncho': ['Turtleneck', 'Jeans', 'Leggings'],
                'Robe': ['Pajamas', 'Onesie'],
            },
        };

        // Reset modal content
        modalContent.innerHTML = '';

        // Find the selected item's label
        const selectedItem = currentWardrobeData[selectedCategory]?.find(item => item._id === selectedItemId);
        if (!selectedItem) {
            modalContent.innerHTML = '<p>Selected item not found.</p>';
            modal.style.display = "block";
            return;
        }

        const selectedItemLabel = selectedItem.classification.label;

        // Get recommended item labels from the recommendationMap
        const recommendedItemLabels = recommendationMap[selectedCategory]?.[selectedItemLabel] || [];

        // Collect recommendations from the wardrobe data
        let recommendations = [];
        recommendedItemLabels.forEach(label => {
            Object.keys(currentWardrobeData).forEach(category => {
                currentWardrobeData[category].forEach(item => {
                    if (item.classification.label === label && item._id !== selectedItemId) {
                        recommendations.push(item);
                    }
                });
            });
        });

        // Display recommendations in modal
        if (recommendations.length > 0) {
            modalContent.innerHTML = `
                <div class="recommendations-grid">
                    ${recommendations.map(item => `
                        <div class="recommendation-item">
                            <img src="${item.image_path}" alt="Recommended Item" />
                            <p>Top Prediction: ${item.classification.label || "Unknown"}</p>
                            <p>Category: ${item.classification.category || "Unknown"}</p>
                        </div>`
                    ).join('')}
                </div>`;
        } else {
            modalContent.innerHTML = '<p>No recommendations found.</p>';
        }

        // Show the modal
        modal.style.display = "block";
    }

    // Weather recommendations
    async function fetchWeatherAndRecommendations() {
        try {
            const response = await fetch("/weather_recommendations");
            const data = await response.json();
            
            if (response.ok && data.weather && data.recommendations) {
                // Clear any existing error messages
                weatherContainer.classList.remove('error');
                
                // Render weather information
                weatherContainer.innerHTML = `
                    <div class="weather-card">
                        <h3>Current Weather</h3>
                        <div class="weather-details">
                            <p><strong>Location:</strong> ${data.weather.city}</p>
                            <p><strong>Temperature:</strong> ${Math.round(data.weather.temperature)}°C</p>
                            <p><strong>Condition:</strong> ${data.weather.condition}</p>
                            <p><strong>Humidity:</strong> ${data.weather.humidity}%</p>
                        </div>
                    </div>
                `;

                // Render weather-based outfit recommendations
                const weatherRecContainer = document.getElementById("weather-recommendations");
                if (data.recommendations.items && data.recommendations.items.length > 0) {
                    weatherRecContainer.innerHTML = `
                        <div class="recommendations-card">
                            <h3>Weather-Appropriate Outfit</h3>
                            
                            <p class="weather-note">${data.recommendations.weatherNote}</p>
                            <div class="weather-outfit-items">
                                ${data.recommendations.items.map(item => `
                                    <div class="recommendation-item">
                                        <img src="${item.image_path}" alt="${item.classification.label}" />
                                        <p class="item-label">${item.classification.label}</p>
                                    </div>
                                `).join('')}
                            </div>
                            ${data.recommendations.missing.length ? `
                                <div class="missing-items">
                                    <p>Suggested additions to your wardrobe:</p>
                                    <ul>
                                        ${data.recommendations.missing.map(item => `<li>${item}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                } else {
                    weatherRecContainer.innerHTML = `
                        <div class="recommendations-card">
                            <h3>Weather-Appropriate Outfit</h3>
                            <p>No suitable items found for current weather. Try adding more items to your wardrobe!</p>
                        </div>
                    `;
                }
            } else if (response.status === 400) {
                weatherContainer.innerHTML = `
                    <div class="weather-error">
                        <p>${data.message || 'Please update your location in your profile to get weather-based recommendations.'}</p>
                        <a href="/profile" class="btn update-location-btn">Update Location</a>
                    </div>
                `;
                document.getElementById("weather-recommendations").innerHTML = '';
            } else {
                throw new Error(data.error || 'Failed to fetch weather data');
            }
        } catch (error) {
            console.error("Error fetching weather:", error);
            weatherContainer.innerHTML = `
                <div class="weather-error">
                    <p>Unable to load weather information. Please try again later.</p>
                </div>
            `;
            document.getElementById("weather-recommendations").innerHTML = '';
        }
    }

    // Schedule next outfit rotation
    function scheduleNextRotation() {
        const now = new Date();
        const nextRotation = new Date(now);
        
        // Set to next 12-hour mark (noon or midnight)
        if (now.getHours() < 12) {
            nextRotation.setHours(12, 0, 0, 0);
        } else {
            nextRotation.setHours(24, 0, 0, 0);
        }
        
        const timeUntilRotation = nextRotation - now;
        
        // Schedule refresh
        setTimeout(() => {
            fetchWeatherAndRecommendations();
            scheduleNextRotation(); // Schedule next rotation
        }, timeUntilRotation);
    }

    // Handle form submission for uploading items
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);

        try {
            const response = await fetch("/upload_item", {
                method: "POST",
                body: formData,
            });
            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                fetchWardrobe();
                uploadForm.reset();
            } else {
                alert(result.error || "Upload failed.");
            }
        } catch (error) {
            console.error("Upload error:", error);
            alert("An error occurred while uploading.");
        }
    });

    // Initialize everything
    fetchWardrobe();
    fetchWeatherAndRecommendations();
    scheduleNextRotation();
});

// Add all required styles
const styles = document.createElement('style');
styles.textContent = `
    .category-group {
        margin-bottom: 2rem;
    }

    .category-items {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .wardrobe-item {
        flex: 0 0 200px;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .wardrobe-item:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .wardrobe-item.selected {
        border-color: #007bff;
        box-shadow: 0 0 0 2px #007bff;
    }

    .wardrobe-item img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 4px;
    }

    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
        overflow-y: auto;
    }

    .modal-content {
        background-color: white;
        margin: 5% auto;
        padding: 20px;
        border-radius: 8px;
        width: 80%;
        max-width: 1000px;
        position: relative;
        animation: modalSlideIn 0.3s ease-out;
    }

    @keyframes modalSlideIn {
        from {
            transform: translateY(-100px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .close-modal {
        position: absolute;
        right: 20px;
        top: 10px;
        font-size: 28px;
        font-weight: bold;
        color: #666;
        cursor: pointer;
    }

    .close-modal:hover {
        color: #000;
    }

    .recommendations-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }

    .recommendation-item {
        text-align: center;
        padding: 10px;
        border: 1px solid #eee;
        border-radius: 8px;
        transition: transform 0.2s;
    }

    .recommendation-item:hover {
        transform: scale(1.02);
    }

    .recommendation-item img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 4px;
        margin-bottom: 10px;
    }

    .weather-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .weather-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }

    .weather-error {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }

    .recommendations-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .weather-outfit-items {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-top: 15px;
    }

    .item-label {
        font-size: 14px;
        color: #333;
    }

    .missing-items {
        margin-top: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
    }

    .missing-items ul {
        margin-top: 10px;
        padding-left: 20px;
    }

    .missing-items li {
        color: #666;
        margin-bottom: 5px;
    }

    .update-location-btn {
        display: inline-block;
        background-color: #007bff;
        color: white;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 4px;
        margin-top: 10px;
        transition: background-color 0.2s;
    }

    .update-location-btn:hover {
        background-color: #0056b3;
    }
`;
document.head.appendChild(styles);