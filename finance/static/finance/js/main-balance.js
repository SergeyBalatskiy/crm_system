document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filter-form');
    const searchInput = document.getElementById('search-input');
    const operationSelect = document.getElementById('history_operation_select');
    const categorySelect = document.getElementById('history_category_select');
    const dateSelect = document.getElementById('history_date_select');
    const customDateRange = document.getElementById('custom-date-range');
    const dateStartInput = document.getElementById('date_start_input');
    const dateEndInput = document.getElementById('date_end_input');
    const btnResetDate = document.getElementById('btn-reset-date');
    const listContainer = document.getElementById('history-list-container');

    let debounceTimer = null;

    // Функция отправки AJAX-запроса
    function fetchFilteredData() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData).toString();
        const url = `${filterForm.action}?${params}`;

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(html => {
                listContainer.innerHTML = html;
            })
            .catch(err => console.error('Ошибка загрузки данных:', err));
    }

    // Задержка (Debounce) 400 мс для текстового поиска
    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchFilteredData();
        }, 400);
    });

    // Мгновенное обновление при смене селектов
    [operationSelect, categorySelect].forEach(select => {
        select.addEventListener('change', fetchFilteredData);
    });

    // Переключение произвольного периода дат
    dateSelect.addEventListener('change', function () {
        if (this.value === 'custom') {
            customDateRange.classList.remove('hidden');
        } else {
            customDateRange.classList.add('hidden');
            dateStartInput.value = '';
            dateEndInput.value = '';
            fetchFilteredData();
        }
    });

    // Реакция на выбор конкретных дат
    [dateStartInput, dateEndInput].forEach(input => {
        input.addEventListener('change', function () {
            if (dateStartInput.value && dateEndInput.value) {
                fetchFilteredData();
            }
        });
    });

    // Сброс диапазона дат обратно к селекту
    btnResetDate.addEventListener('click', function () {
        customDateRange.classList.add('hidden');
        dateSelect.value = '';
        dateStartInput.value = '';
        dateEndInput.value = '';
        fetchFilteredData();
    });
});