document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // 1. ИНИЦИАЛИЗАЦИЯ И АВТОСКРЫТИЕ СООБЩЕНИЙ (ПРИ РЕДИРЕКТЕ)
    // ==========================================
    function initFlashMessages() {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const alerts = container.querySelectorAll('.alert');
        alerts.forEach(alert => {
            // Добавляем обработчик клика на кнопку закрытия (крестик)
            const closeBtn = alert.querySelector('.alert-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => dismissAlert(alert));
            }

            // Автоматическое скрытие через 4 секунды
            setTimeout(() => dismissAlert(alert), 4000);
        });
    }

    function dismissAlert(alert) {
        if (!alert || alert.classList.contains('fade-out')) return;
        alert.classList.add('fade-out');
        setTimeout(() => alert.remove(), 300); // 300ms совпадает с анимацией в CSS
    }

    // Запускаем обработку входящих сообщений
    initFlashMessages();


    // ==========================================
    // 2. ФИЛЬТРАЦИЯ И КАЛЕНДАРЬ
    // ==========================================
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

    // Главная функция отправки AJAX для фильтрации
    function fetchFilteredData() {
        if (!filterForm || !listContainer) return;

        const startVal = dateStartInput.value;
        const endVal = dateEndInput.value;

        if (!customDateRange.classList.contains('hidden')) {
            const isStartValid = isValidFullDate(startVal);
            const isEndValid = isValidFullDate(endVal);

            dateStartInput.classList.toggle('error', !isStartValid);
            dateEndInput.classList.toggle('error', !isEndValid);

            if (!isStartValid || !isEndValid) return;

            if (startVal && endVal && startVal > endVal) {
                dateStartInput.classList.add('error');
                dateEndInput.classList.add('error');
                return;
            }
        }

        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
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
                formatNumbers(listContainer);
            })
            .catch(error => console.error('Ошибка фильтрации:', error));
    }

    // --- Переключение режимов даты ---
    if (dateSelect) {
        dateSelect.addEventListener('change', () => {
            if (dateSelect.value === 'custom') {
                dateSelect.classList.add('hidden');
                customDateRange.classList.remove('hidden');
            } else {
                fetchFilteredData();
            }
        });
    }

    if (btnResetDate) {
        btnResetDate.addEventListener('click', () => {
            dateStartInput.value = '';
            dateEndInput.value = '';
            dateStartInput.classList.remove('error');
            dateEndInput.classList.remove('error');

            customDateRange.classList.add('hidden');
            dateSelect.classList.remove('hidden');

            dateSelect.value = '';
            fetchFilteredData();
        });
    }

    // --- События ввода ---
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchFilteredData, 300);
        });
    }

    if (operationSelect) {
        operationSelect.addEventListener('change', fetchFilteredData);
    }

    [dateStartInput, dateEndInput].forEach(input => {
        if (input) {
            input.addEventListener('change', fetchFilteredData);
            input.addEventListener('input', () => {
                if (isValidFullDate(input.value)) {
                    fetchFilteredData();
                }
            });
        }
    });

    // Форматирование разрядов чисел при загрузке
    formatNumbers();
});

// ==========================================
// 3. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ФОРМАТИРОВАНИЯ
// ==========================================
function formatNumbers(container = document) {
    container.querySelectorAll('.format-num').forEach(el => {
        let rawVal = el.dataset.raw || el.textContent.trim();
        if (!el.dataset.raw) el.dataset.raw = rawVal;

        if (rawVal) {
            el.textContent = rawVal.replace(/\d+/g, chunk =>
                chunk.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
            );
        }
    });
}