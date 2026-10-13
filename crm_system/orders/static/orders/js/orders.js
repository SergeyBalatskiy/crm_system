function openOrderDrawer() {
    document.getElementById('order-drawer').classList.add('active');
    document.getElementById('drawer-overlay').classList.add('active');
    document.body.style.overflow = 'hidden'; // Блокируем прокрутку основной страницы
}

function closeOrderDrawer() {
    document.getElementById('order-drawer').classList.remove('active');
    document.getElementById('drawer-overlay').classList.remove('active');
    document.body.style.overflow = ''; // Возвращаем прокрутку
}

// Закрытие по нажатию клавиши ESC
document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        closeOrderDrawer();
    }
});

// Показать подсказки при клике/фокусе
function showHints(input) {
    // Закрываем все другие открытые подсказки
    document.querySelectorAll('.custom-hints-dropdown').forEach(d => d.style.display = 'none');

    const dropdown = input.nextElementSibling;
    if (dropdown && dropdown.children.length > 0) {
        dropdown.style.display = 'block';
    }
}

// Фильтрация при наборе текста
function filterHints(input) {
    const filter = input.value.toLowerCase();
    const dropdown = input.nextElementSibling;
    const items = dropdown.querySelectorAll('li');

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(filter) ? 'block' : 'none';
    });

    dropdown.style.display = 'block';
}

// Выбор варианта из списка
function selectHint(li, value) {
    const input = li.closest('.custom-autocomplete-wrapper').querySelector('input');
    const currentValue = input.value.trim();

    if (currentValue) {
        // Разделяем уже введенные значения по запятой, чтобы проверить на дубликаты
        const items = currentValue.split(',').map(item => item.trim());

        // Если такого значения еще нет в инпуте, добавляем его через запятую
        if (!items.includes(value)) {
            input.value = currentValue + ', ' + value;
        }
    } else {
        // Если поле было пустым, просто записываем значение
        input.value = value;
    }

    // Скрываем список подсказок после выбора
    li.parentElement.style.display = 'none';
}

// Закрытие подсказок при клике вне поля
document.addEventListener('click', function (e) {
    if (!e.target.closest('.custom-autocomplete-wrapper')) {
        document.querySelectorAll('.custom-hints-dropdown').forEach(d => d.style.display = 'none');
    }
});

// Переключение видимости поля предоплаты
function togglePrepayInput(checkbox) {
    const container = document.getElementById('prepay-amount-container');
    const input = document.getElementById('prepay-amount-input');

    if (checkbox.checked) {
        container.style.display = 'block';
        input.focus();
    } else {
        container.style.display = 'none';
        input.value = ''; // сбрасываем значение при выключении
    }
}

// Форматирование числа с разделителями тысяч (1 000, 2 500)
function formatMoneyInput(input) {
    // Оставляем только цифры
    let value = input.value.replace(/\D/g, '');
    if (value) {
        // Превращаем в число и форматируем по русской локали (с пробелами)
        value = Number(value).toLocaleString('ru-RU');
    }
    input.value = value;
}

// Перед отправкой формы убираем пробелы из суммы, чтобы бэкенд получил чистое число
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('create-order-form');
    if (form) {
        form.addEventListener('submit', function () {
            const prepayInput = document.getElementById('prepay-amount-input');
            if (prepayInput && prepayInput.value) {
                prepayInput.value = prepayInput.value.replace(/\s/g, '');
            }
        });
    }
});

function handleClientFocus(currentInput) {
    // Определяем, какое поле сейчас в фокусе, а какое — соседнее
    const fieldName = currentInput.name;
    const oppositeFieldKey = fieldName === 'name' ? 'phone' : 'name';

    // Находим блок подсказок противоположного поля и очищаем его
    const oppositeDropdown = document.getElementById('suggestions-' + oppositeFieldKey);
    if (oppositeDropdown) {
        oppositeDropdown.innerHTML = '';
    }
}

function toggleDateRange(select) {
    const rangeWrapper = document.getElementById('custom-date-range');
    if (select.value === 'custom') {
        rangeWrapper.classList.remove('hidden');
    } else {
        rangeWrapper.classList.add('hidden');
        // Очищаем интуитивно даты при скрытии, чтобы не мешали фильтрации
        document.getElementById('date_start_input').value = '';
        document.getElementById('date_end_input').value = '';
        // Триггерим событие change на форме, чтобы HTMX отправил запрос сброса дат
        htmx.trigger('#filter-form', 'change');
    }
}

function resetDateRange() {
    const select = document.getElementById('history_date_select');
    select.value = '';
    toggleDateRange(select);
}

// Автоматически очищаем форму при обычной загрузке/перезагрузке страницы, если в URL нет параметров
document.addEventListener("DOMContentLoaded", function () {
    if (!window.location.search) {
        const form = document.getElementById('filter-form');
        if (form) {
            form.reset();
        }
    }
});

function toggleDateRange(select) {
    const rangeWrapper = document.getElementById('custom-date-range');
    if (select.value === 'custom') {
        rangeWrapper.classList.remove('hidden');
    } else {
        rangeWrapper.classList.add('hidden');
        document.querySelector('input[name="date_start_input"]').value = '';
        document.querySelector('input[name="date_end_input"]').value = '';
        htmx.trigger('#filter-form', 'change');
    }
}

function resetDateRange() {
    const select = document.getElementById('history_date_select');
    select.value = '';
    toggleDateRange(select);
}