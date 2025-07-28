document.addEventListener('DOMContentLoaded', () => {
  const categories = document.querySelectorAll('.category');
  const container = document.querySelector('.feeds-container');

  // Restore order from localStorage
  const savedOrder = JSON.parse(localStorage.getItem('categoryOrder')) || [];
  if (savedOrder.length > 0) {
    savedOrder.forEach(id => {
      const category = document.getElementById(id);
      if (category) {
        container.appendChild(category);
      }
    });
  }

  categories.forEach(category => {
    category.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', category.id);
      category.classList.add('dragging');
    });

    category.addEventListener('dragend', () => {
      category.classList.remove('dragging');
      saveOrder();
    });
  });

  container.addEventListener('dragover', (e) => {
    e.preventDefault();
    const draggingCategory = document.querySelector('.dragging');
    const afterElement = getDragAfterElement(container, e.clientY);
    if (afterElement == null) {
      container.appendChild(draggingCategory);
    } else {
      container.insertBefore(draggingCategory, afterElement);
    }
  });

  function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.category:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }

  function saveOrder() {
    const order = [...container.querySelectorAll('.category')].map(category => category.id);
    localStorage.setItem('categoryOrder', JSON.stringify(order));
  }
});