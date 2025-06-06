const container = document.getElementById('image-preview');

container.addEventListener('click', (e) => {
  if (e.target.classList.contains('delete-btn')) {
    const wrapper = e.target.closest('.image-wrapper');
    if (wrapper) {
      wrapper.remove();
    }
  }
});

// On form submit, send the list of images still shown to backend:
const form = document.querySelector('form');
form.addEventListener('submit', (e) => {
  let input = form.querySelector('input[name="remaining_images"]');
  if (!input) {
    input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'remaining_images';
    form.appendChild(input);
  }
  // Collect all remaining images in their original order
  const remainingImages = Array.from(container.querySelectorAll('img'))
    .map(img => img.dataset.image);
  input.value = JSON.stringify(remainingImages);
});
