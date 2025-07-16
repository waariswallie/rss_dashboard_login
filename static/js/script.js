document.addEventListener("DOMContentLoaded", () => {
  const columns = document.querySelectorAll(".column");

  columns.forEach(col => {
    col.addEventListener("dragstart", (e) => {
      col.classList.add("dragging");
      e.dataTransfer.setData("text/plain", col.dataset.title);
    });

    col.addEventListener("dragend", () => {
      col.classList.remove("dragging");
    });
  });

  const containers = document.querySelectorAll(".columns");
  containers.forEach(container => {
    container.addEventListener("dragover", (e) => {
      e.preventDefault();
      const dragging = document.querySelector(".dragging");
      const afterElement = getDragAfterElement(container, e.clientX);
      if (afterElement == null) {
        container.appendChild(dragging);
      } else {
        container.insertBefore(dragging, afterElement);
      }
    });
  });

  function getDragAfterElement(container, x) {
    const draggableElements = [...container.querySelectorAll(".column:not(.dragging)")];
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = x - box.left - box.width / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }

  // automatische verversing
  setInterval(() => {
    window.location.reload();
  }, 300000);
});
