document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('filter-form');
    const container = document.getElementById('history-list-container');

    function fetchFilteredData() {
        const formData = new FormData(form);
        const searchParams = new URLSearchParams(formData).toString();

        fetch(`${form.action}?${searchParams}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html; // Заменяем список карточек новыми данными
            });
    }

    // Слушаем изменения в селектах и ввод в инпуте
    form.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', fetchFilteredData);
    });

    let timeout = null;
    document.getElementById('search-input').addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(fetchFilteredData, 300); // Задержка 300мс при печати (дебаунс)
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const searchInput = document.getElementById('search-input');
    const operationSelect = document.getElementById('history_operation_select');

    // Элементы даты
    const dateSelect = document.getElementById('history_date_select');
    const customDateRange = document.getElementById('custom-date-range');
    const dateStartInput = document.getElementById('date_start_input');
    const dateEndInput = document.getElementById('date_end_input');
    const btnResetDate = document.getElementById('btn-reset-date');

    const listContainer = document.getElementById('history-list-container');

    let debounceTimer;

    // Вспомогательная функция проверки полноты даты (YYYY-MM-DD)
    function isValidFullDate(dateString) {
        if (!dateString) return true;
        return /^\d{4}-\d{2}-\d{2}$/.test(dateString);
    }

    // Главная функция отправки AJAX
    function fetchFilteredData() {
        const startVal = dateStartInput.value;
        const endVal = dateEndInput.value;

        // Проверяем валидность дат, если открыт календарь
        if (!customDateRange.classList.contains('hidden')) {
            const isStartValid = isValidFullDate(startVal);
            const isEndValid = isValidFullDate(endVal);

            dateStartInput.classList.toggle('error', !isStartValid);
            dateEndInput.classList.toggle('error', !isEndValid);

            // Если одна из дат заполнена не полностью — отменяем отправку
            if (!isStartValid || !isEndValid) return;

            // Если "От" больше чем "До" — отменяем
            if (startVal && endVal && startVal > endVal) {
                dateStartInput.classList.add('error');
                dateEndInput.classList.add('error');
                return;
            }
        }

        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            // Не передаем значение "custom", чтобы не сбивать бэкенд
            if (value && value !== 'custom') {
                params.append(key, value);
            }
        }

        const url = `${filterForm.action}?${params.toString()}`;

        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сервера');
                return response.text();
            })
            .then(html => {
                listContainer.innerHTML = html;
            })
            .catch(error => console.error('Ошибка фильтрации:', error));
    }

    // --- ПЕРЕКЛЮЧЕНИЕ РЕЖИМОВ ДАТЫ ---

    // 1. При выборе "Указать период..." переключаем на календарь
    dateSelect.addEventListener('change', () => {
        if (dateSelect.value === 'custom') {
            dateSelect.classList.add('hidden');
            customDateRange.classList.remove('hidden');
        } else {
            fetchFilteredData();
        }
    });

    // 2. Нажатие на крестик — возврат к обычным пресетам
    btnResetDate.addEventListener('click', () => {
        // Очищаем календарь
        dateStartInput.value = '';
        dateEndInput.value = '';
        dateStartInput.classList.remove('error');
        dateEndInput.classList.remove('error');

        // Переключаем видимость
        customDateRange.classList.add('hidden');
        dateSelect.classList.remove('hidden');

        // Сбрасываем селект на "За всё время" и запрашиваем данные
        dateSelect.value = '';
        fetchFilteredData();
    });

    // --- СОБЫТИЯ ВВОДА ---

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchFilteredData, 300);
    });

    operationSelect.addEventListener('change', fetchFilteredData);

    // События ввода для календаря
    [dateStartInput, dateEndInput].forEach(input => {
        input.addEventListener('change', fetchFilteredData);
        input.addEventListener('input', () => {
            if (isValidFullDate(input.value)) {
                fetchFilteredData();
            }
        });
    });
});