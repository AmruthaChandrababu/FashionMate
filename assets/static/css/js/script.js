document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:5000';
    const DEFAULT_USER_ID = 'user123';
  
    const wardrobeGrid = document.getElementById('wardrobe-grid');
    const clothingUpload = document.getElementById('clothing-upload');
    const recommendationsContainer = document.querySelector('.recommendations-container');
  
    // Upload clothing
    clothingUpload.addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', DEFAULT_USER_ID);
  
        try {
          const response = await fetch(`${API_BASE_URL}/upload_clothing`, {
            method: 'POST',
            body: formData,
          });
  
          const result = await response.json();
          if (response.ok) {
            alert('Clothing uploaded successfully!');
            fetchWardrobe(); // Refresh wardrobe items
          } else {
            alert(`Error: ${result.error}`);
          }
        } catch (error) {
          console.error('Error uploading clothing:', error);
        }
      }
    });
  
    // Fetch and render wardrobe
    async function fetchWardrobe() {
      try {
        const response = await fetch(`${API_BASE_URL}/user/wardrobe?user_id=${DEFAULT_USER_ID}`);
        const data = await response.json();
        if (response.ok) {
          renderWardrobe(data.wardrobe);
        } else {
          alert(`Error: ${data.error}`);
        }
      } catch (error) {
        console.error('Error fetching wardrobe:', error);
      }
    }
  
    function renderWardrobe(items) {
      wardrobeGrid.innerHTML = items.map(
        (item) => `
        <div class="wardrobe-item">
          <img src="${API_BASE_URL}/uploads/${item.filename}" alt="${item.filename}">
          <p>${item.category || 'Uncategorized'}</p>
        </div>`
      ).join('');
    }
  
    // Fetch and render recommendations
    async function fetchRecommendations() {
      try {
        const response = await fetch(`${API_BASE_URL}/recommendations?user_id=${DEFAULT_USER_ID}`);
        const data = await response.json();
        if (response.ok) {
          renderRecommendations(data.recommendations);
        } else {
          alert(`Error: ${data.error}`);
        }
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      }
    }
  
    function renderRecommendations(recommendations) {
      recommendationsContainer.innerHTML = recommendations.map(
        (rec) => `
        <div class="recommendation-card">
          <img src="${API_BASE_URL}/uploads/${rec.filename}" alt="${rec.filename}">
          <p>${rec.category || 'Recommended Outfit'}</p>
        </div>`
      ).join('');
    }
  
    // Initialize
    fetchWardrobe();
    fetchRecommendations();
  });
  