const selected = {
  country: [],
  city: [],
  category: null,
};

const params = new URLSearchParams(window.location.search);

// Инициализация из URL
selected.country = params.getAll('country');
selected.city = params.getAll('city');
selected.category = params.get('category');

// Установка active-классов
function updateButtonStates() {
  document.querySelectorAll('button[data-type="country"]').forEach(btn => {
    btn.classList.toggle('active', selected.country.includes(btn.dataset.value));
  });

  document.querySelectorAll('button[data-type="city"]').forEach(btn => {
    btn.classList.toggle('active', selected.city.includes(btn.dataset.value));
  });

  document.querySelectorAll('button[data-type="category"]').forEach(btn => {
    btn.classList.toggle('active', selected.category === btn.dataset.value);
  });
}

// ✅ Обновить URL и перезагрузить (фильтр меняется → offset сбрасывается)
function applyFilters() {
  const url = new URL(window.location.href);
  const sp = url.searchParams;

  sp.delete("country");
  sp.delete("city");
  sp.delete("category");
  sp.delete("offset"); // сброс пагинации

  selected.country.forEach(c => sp.append("country", c));
  selected.city.forEach(c => sp.append("city", c));
  if (selected.category) sp.set("category", selected.category);

  // Добавляем from_date и until_date, если заданы
  const from = document.getElementById("from_date")?.value;
  const until = document.getElementById("until_date")?.value;

  if (from) sp.set("from_date", from);
  if (until) sp.set("until_date", until);

  window.location.href = `${url.pathname}?${sp.toString()}`;
}

// Обработчики кнопок-фильтров
document.querySelectorAll('button[data-type]').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    const value = btn.dataset.value;

    if (type === 'category') {
      selected.category = selected.category === value ? null : value;
    } else {
      const idx = selected[type].indexOf(value);
      if (idx >= 0) {
        selected[type].splice(idx, 1);
      } else {
        selected[type].push(value);
      }
    }

    applyFilters(); // при клике сразу обновляем URL
  });
});

// Очистка конкретного фильтра
function clearParam(param) {
  const url = new URL(window.location.href);
  url.searchParams.delete(param);
  url.searchParams.delete('offset');
  window.location.href = url.toString();
}

document.getElementById("clear-category")?.addEventListener("click", () => clearParam('category'));
document.getElementById("clear-city")?.addEventListener("click", () => clearParam('city'));
document.getElementById("clear-country")?.addEventListener("click", () => clearParam('country'));

// Подсветка активных кнопок при загрузке
window.addEventListener('DOMContentLoaded', updateButtonStates);

// Удаление пустых инпутов при сабмите
document.getElementById('filter-form')?.addEventListener('submit', function () {
  this.querySelectorAll('input').forEach(input => {
    if (!input.value.trim()) input.remove();
  });
});
