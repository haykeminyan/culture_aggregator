document.addEventListener('DOMContentLoaded', () => {
  // --- Инициализация выбранных фильтров из URL ---
  const selected = {
    country: [],
    city: [],
    category: null,
  };

  const params = new URLSearchParams(window.location.search);
  selected.country = params.getAll('country');
  selected.city = params.getAll('city');
  selected.category = params.get('category');

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

    const from = document.getElementById("from_date")?.value;
    const until = document.getElementById("until_date")?.value;
    if (from) sp.set("from_date", from);
    if (until) sp.set("until_date", until);

    const search = document.getElementById("search")?.value?.trim();
    if (search) {
      sp.set("search", search);
    } else {
      sp.delete("search");
    }

    window.location.href = `${url.pathname}?${sp.toString()}`;
  }

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

      applyFilters();
    });
  });

  function clearParam(param) {
    const url = new URL(window.location.href);
    url.searchParams.delete(param);
    url.searchParams.delete('offset');
    window.location.href = url.toString();
  }

  document.getElementById("clear-category")?.addEventListener("click", () => clearParam('category'));
  document.getElementById("clear-city")?.addEventListener("click", () => clearParam('city'));
  document.getElementById("clear-country")?.addEventListener("click", () => clearParam('country'));

  // --- Логика показа кнопок с "Show more" ---
  const batchSize = 20;

  // Страны
  const allCountryButtons = Array.from(document.querySelectorAll('button[data-type="country"]'));
  const loadMoreCountryBtn = document.getElementById('load-more-countries');
  const activeCountries = new Set(selected.country);
  let countryPool = [];

  allCountryButtons.forEach(btn => btn.style.display = 'none');
  allCountryButtons.forEach(btn => {
    if (activeCountries.has(btn.dataset.value)) {
      btn.style.display = 'inline-block';
      btn.dataset.forceVisible = 'true';
    } else {
      countryPool.push(btn);
    }
  });

  function showNextBatchCountries() {
    const nextBatch = countryPool.splice(0, batchSize);
    nextBatch.forEach(btn => btn.style.display = 'inline-block');

    if (countryPool.length === 0) {
      loadMoreCountryBtn.style.display = 'none';
    }
  }

  showNextBatchCountries();

  loadMoreCountryBtn?.addEventListener('click', e => {
    e.preventDefault();
    showNextBatchCountries();
  });

  // Города
  const allCityButtons = Array.from(document.querySelectorAll('button[data-type="city"]'));
  const loadMoreCityBtn = document.getElementById('load-more-cities');
  const activeCities = new Set(selected.city);
  let cityPool = [];

  allCityButtons.forEach(btn => btn.style.display = 'none');
  allCityButtons.forEach(btn => {
    if (activeCities.has(btn.dataset.value)) {
      btn.style.display = 'inline-block';
      btn.dataset.forceVisible = 'true';
    } else {
      cityPool.push(btn);
    }
  });

  function showNextBatchCities() {
    const nextBatch = cityPool.splice(0, batchSize);
    nextBatch.forEach(btn => btn.style.display = 'inline-block');

    if (cityPool.length === 0) {
      loadMoreCityBtn.style.display = 'none';
    }
  }

  showNextBatchCities();

  loadMoreCityBtn?.addEventListener('click', e => {
    e.preventDefault();
    showNextBatchCities();
  });

  // Категории
  const allCategoryButtons = Array.from(document.querySelectorAll('button[data-type="category"]'));
  const loadMoreCategoryBtn = document.getElementById('load-more-categories');
  const activeCategory = selected.category;
  let categoryPool = [];

  allCategoryButtons.forEach(btn => btn.style.display = 'none');
  allCategoryButtons.forEach(btn => {
    if (activeCategory === btn.dataset.value) {
      btn.style.display = 'inline-block';
      btn.dataset.forceVisible = 'true';
    } else {
      categoryPool.push(btn);
    }
  });

  function showNextBatchCategories() {
    const nextBatch = categoryPool.splice(0, batchSize);
    nextBatch.forEach(btn => btn.style.display = 'inline-block');

    if (categoryPool.length === 0) {
      loadMoreCategoryBtn.style.display = 'none';
    }
  }

  showNextBatchCategories();

  loadMoreCategoryBtn?.addEventListener('click', e => {
    e.preventDefault();
    showNextBatchCategories();
  });

  // --- Подсвечиваем активные кнопки (после инициализации показа) ---
  updateButtonStates();
});