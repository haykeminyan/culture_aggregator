const selected = {
  country: null,
  city: null,
  category: null,
};

document.querySelectorAll('button[data-type]').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    const value = btn.dataset.value;

    // Снять активные в этой группе
    document.querySelectorAll(`button[data-type="${type}"]`).forEach(b => b.classList.remove('active'));

    // Если уже выбрано это же значение — снимаем
    if (selected[type] === value) {
      selected[type] = null;
    } else {
      selected[type] = value;
      btn.classList.add('active');
    }

    updateHiddenInputs();
  });
});

function updateHiddenInputs() {
  const container = document.getElementById('hidden-filters');
  container.innerHTML = '';

  Object.entries(selected).forEach(([key, value]) => {
    if (value) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      container.appendChild(input);
    }
  });
}

// Первичная инициализация
updateHiddenInputs();

// Удаляем пустые поля только у type="text" и hidden (оставляем даты!)
document.getElementById('filter-form').addEventListener('submit', function () {
  this.querySelectorAll('input[name]').forEach(input => {
    const isSafe = input.type === 'text' || input.type === 'hidden';
    if (isSafe && !input.value.trim()) {
      input.remove();
    }
  });
});

// Очистка каждого фильтра по кнопке
document.getElementById("clear-category").addEventListener("click", function () {
  const url = new URL(window.location.href);
  url.searchParams.delete("category");
  window.location.href = url.toString();
});

document.getElementById("clear-city").addEventListener("click", function () {
  const url = new URL(window.location.href);
  url.searchParams.delete("city");
  window.location.href = url.toString();
});

document.getElementById("clear-country").addEventListener("click", function () {
  const url = new URL(window.location.href);
  url.searchParams.delete("country");
  window.location.href = url.toString();
});
