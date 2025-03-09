// Handle the file input change event and display selected images in preview
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('file-preview');
const wardrobeGallery = document.getElementById('wardrobe-gallery');

fileInput.addEventListener('change', (event) => {
    // Clear previous previews
    filePreview.innerHTML = '';

    // Loop through selected files and display image previews
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function (e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = file.name;
            filePreview.appendChild(img);

            // Add the image to wardrobe-gallery
            const wardrobeItem = document.createElement('div');
            wardrobeItem.classList.add('wardrobe-item');
            wardrobeItem.appendChild(img);
            wardrobeGallery.appendChild(wardrobeItem);
        };

        reader.readAsDataURL(file);
    }
});

// Optional: Handle the Upload button click (You can add functionality to handle form submission or storage)
document.getElementById('uploadButton').addEventListener('click', () => {
    alert('Items added to your wardrobe!');
});
