const selected = {
  country: [],
  city: [],
  category: null,
};

function getUrlParamsArray(name) {
  const params = new URLSearchParams(window.location.search);
  return params.getAll(name);
}

// Инициализируем selected из URL
selected.country = getUrlParamsArray('country');
selected.city = getUrlParamsArray('city');
const categoryFromUrl = new URLSearchParams(window.location.search).get('category');
selected.category = categoryFromUrl ? categoryFromUrl : null;

document.querySelectorAll('button[data-type]').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    const value = btn.dataset.value;

    if (type === 'category') {
      if (selected.category === value) {
        selected.category = null;
        btn.classList.remove('active');
      } else {
        document.querySelectorAll('button[data-type="category"]').forEach(b => b.classList.remove('active'));
        selected.category = value;
        btn.classList.add('active');
      }
    } else {
      const index = selected[type].indexOf(value);
      if (index > -1) {
        selected[type].splice(index, 1);
        btn.classList.remove('active');
      } else {
        selected[type].push(value);
        btn.classList.add('active');
      }
    }

    updateHiddenInputs();
  });
});

function updateHiddenInputs() {
  const container = document.getElementById('hidden-filters');
  container.innerHTML = '';

  Object.entries(selected).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(v => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = v;
        container.appendChild(input);
      });
    } else if (value) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      container.appendChild(input);
    }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  if (selected.category) {
    document.querySelectorAll('button[data-type="category"]').forEach(btn => {
      if (btn.dataset.value === selected.category) btn.classList.add('active');
    });
  }
  ['country', 'city'].forEach(type => {
    selected[type].forEach(val => {
      document.querySelectorAll(`button[data-type="${type}"]`).forEach(btn => {
        if (btn.dataset.value === val) btn.classList.add('active');
      });
    });
  });
  updateHiddenInputs();
});

document.getElementById('filter-form').addEventListener('submit', function (e) {
  this.querySelectorAll('input').forEach(input => {
    if (!input.value.trim()) {
      input.name = '';
    }
  });
});

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
