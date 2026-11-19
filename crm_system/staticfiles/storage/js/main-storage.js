document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const searchInput = document.getElementById('search-input');
    const toggleInput = document.getElementById('min-items-toggle');
    const dateStartInput = document.getElementById('date_start_input');
    const dateEndInput = document.getElementById('date_end_input');
    const listContainer = document.getElementById('main-list-container');

    let debounceTimer;

    // Вспомогательная функция проверки корректности даты (формат YYYY-MM-DD)
    function isValidFullDate(dateString) {
        if (!dateString) return true; // Пустая дата допускается
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        return dateRegex.test(dateString);
    }

    // Функция отправки AJAX-запроса
    function fetchFilteredData() {
        const startVal = dateStartInput.value;
        const endVal = dateEndInput.value;

        // Валидация дат: проверяем, что они полностью заполнены, а не частично
        const isStartValid = isValidFullDate(startVal);
        const isEndValid = isValidFullDate(endVal);

        // Подсвечиваем ошибки, если дата введена не полностью
        dateStartInput.classList.toggle('error', !isStartValid);
        dateEndInput.classList.toggle('error', !isEndValid);

        // Если хотя бы одна дата заполнена не полностью (напр. "01.09.____") — не отправляем запрос
        if (!isStartValid || !isEndValid) {
            return;
        }

        // Если введены обе даты, проверяем чтобы "От" не была позже "До"
        if (startVal && endVal && startVal > endVal) {
            dateStartInput.classList.add('error');
            dateEndInput.classList.add('error');
            return;
        }

        // Собираем параметры формы
        const formData = new FormData(filterForm);

        // Корректная обработка чекбокса для GET-запроса
        const params = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value) {
                params.append(key, value);
            }
        }

        const url = `${filterForm.action}?${params.toString()}`;

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сервера при фильтрации');
                }
                return response.text();
            })
            .then(html => {
                listContainer.innerHTML = html;
                formatNumbers(listContainer);
            })
            .catch(error => {
                console.error('Ошибка AJAX:', error);
            });
    }

    // 1. Поиск с дебаунсом (300 мс)
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchFilteredData, 300);
    });

    // 2. Клик по тумблеру "Мало на складе"
    toggleInput.addEventListener('change', fetchFilteredData);

    // 3. Выбор дат
    dateStartInput.addEventListener('change', fetchFilteredData);
    dateEndInput.addEventListener('change', fetchFilteredData);

    // Событие 'input' на датах защищает от попытки ввода недописанных значений с клавиатуры
    dateStartInput.addEventListener('input', () => {
        if (isValidFullDate(dateStartInput.value)) {
            fetchFilteredData();
        }
    });
    dateEndInput.addEventListener('input', () => {
        if (isValidFullDate(dateEndInput.value)) {
            fetchFilteredData();
        }
    });
});

// Вспомогательная функция форматирования тысяч
function formatNumbers(container = document) {
    container.querySelectorAll('.format-num').forEach(el => {
        let rawVal = el.dataset.raw || el.textContent.trim();
        if (!el.dataset.raw) el.dataset.raw = rawVal;

        if (rawVal) {
            // Разделяем каждые 3 цифры пробелом (10000 -> 10 000)
            el.textContent = rawVal.replace(/\d+/g, chunk =>
                chunk.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
            );
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Форматируем при первичной загрузке страницы
    formatNumbers();
});