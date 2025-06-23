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

document.getElementById('filter-form').addEventListener('submit', function (e) {
  // Удаляем пустые поля из формы, чтобы они не отправлялись
  this.querySelectorAll('input').forEach(input => {
    console.log(input.value)
    if (!input.value.trim()) {
      input.name = ''; // убираем name, поле не попадет в GET-запрос
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
