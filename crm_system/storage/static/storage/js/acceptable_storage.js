document.addEventListener('DOMContentLoaded', function () {
    const addFormBtn = document.getElementById('add-new-form-acceptable');
    const formsList = document.getElementById('acceptable-div-form');
    const formContainer = document.getElementById('form-container');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    const emptyFormTemplate = document.getElementById('empty-form-acceptable').innerHTML;

    // Списoк полей, требующих форматирования тысячных
    const numberFieldNames = [
        'quantity_at_the_purchase',
        'buy_price',
        'retail_price',
        'minimum_items_for_notification'
    ];

    // Вспомогательная функция проверки имени поля
    function isTargetNumberInput(input) {
        if (!input || !input.name) return false;
        return numberFieldNames.some(field => input.name.includes(field));
    }

    // Форматирование числа с пробелами
    function formatThousands(value) {
        if (!value) return '';
        let clean = value.toString().replace(/\D/g, '');
        return clean.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    // Применение маски тысячи к конкретному инпуту
    function setupNumericInput(input) {
        if (!isTargetNumberInput(input)) return;

        // Переводим из type="number" в type="text", чтобы браузер разрешил пробелы
        input.type = 'text';
        input.setAttribute('inputmode', 'numeric');
        input.setAttribute('autocomplete', 'off');

        if (input.value) {
            input.value = formatThousands(input.value);
        }

        input.addEventListener('input', function () {
            let cursorPosition = this.selectionStart;
            let originalLength = this.value.length;

            let cleanVal = this.value.replace(/\D/g, '');

            if (cleanVal === '') {
                this.value = '';
                return;
            }

            let formatted = cleanVal.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
            this.value = formatted;

            // Восстановление корректной позиции курсора
            let newLength = formatted.length;
            cursorPosition += (newLength - originalLength);
            this.setSelectionRange(cursorPosition, cursorPosition);
        });
    }

    // Инициализация существующих инпутов
    document.querySelectorAll('#acceptable-div-form input').forEach(setupNumericInput);

    // Обновление нумерации столбца #
    function updateRowNumbers() {
        const rows = document.querySelectorAll('#acceptable-div-form tr.item-row');
        rows.forEach((row, index) => {
            const numCell = row.querySelector('.row-number .hash');
            if (numCell) numCell.textContent = index + 1;
        });
    }

    // 1. ДОБАВЛЕНИЕ СТРОКИ
    if (addFormBtn && formsList && totalFormsInput) {
        addFormBtn.addEventListener('click', function () {
            let currentFormCount = parseInt(totalFormsInput.value, 10) || formsList.querySelectorAll('tr.item-row').length;

            const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, currentFormCount);
            formsList.insertAdjacentHTML('beforeend', newFormHtml);

            totalFormsInput.value = currentFormCount + 1;
            updateRowNumbers();

            // Подключаем форматирование тысячных к новым полям
            const $lastRow = $('#acceptable-div-form tr.item-row:last-child');
            $lastRow.find('input').each(function () {
                setupNumericInput(this);
            });

            // Инициализация Select2 для нового селекта
            setTimeout(function () {
                const $sel = $lastRow.find('select');
                if ($sel.length && typeof $sel.select2 === 'function') {
                    $sel.select2({
                        ajax: {
                            url: $sel.attr('data-autocomplete-light-url') || '/storage/storage-autocomplete',
                            dataType: 'json',
                            delay: 250,
                            data: function (params) {
                                return { q: params.term };
                            },
                            processResults: function (data) {
                                return { results: data.results || data };
                            },
                            cache: true
                        },
                        placeholder: $sel.attr('data-placeholder') || 'Начните вводить название...',
                        allowClear: true,
                        width: '100%'
                    });
                }
            }, 100);
        });
    }

    // 2. УДАЛЕНИЕ СТРОКИ
    document.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('btn-remove-row')) {
            const row = e.target.closest('tr');
            const rows = formsList ? formsList.querySelectorAll('tr.item-row') : [];

            if (row && rows.length > 1) {
                const $select = $(row).find('select');
                if ($select.length && $select.data('select2')) {
                    $select.select2('destroy');
                }

                row.remove();
                if (totalFormsInput) {
                    totalFormsInput.value = formsList.querySelectorAll('tr.item-row').length;
                }
                updateRowNumbers();
            }
        }
    });

    // 3. ОЧИСТКА ПРОБЕЛОВ ПЕРЕД ОТПРАВКОЙ НА БЭКЕНД
    if (formContainer) {
        formContainer.addEventListener('submit', function () {
            const inputs = formContainer.querySelectorAll('input');
            inputs.forEach(input => {
                if (isTargetNumberInput(input)) {
                    input.value = input.value.replace(/\s+/g, '');
                }
            });
        });
    }

    // 4. ИСЧЕЗАЮЩИЕ СООБЩЕНИЯ (FLASH MESSAGES)
    function autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.classList.add('fade-out');
                setTimeout(() => alert.remove(), 400);
            }, 4000); // Сообщение исчезает через 4 секунды
        });
    }
    autoDismissAlerts();

    // 5. ОБРАБОТЧИК СООБЩЕНИЙ ОТ БЭКЕНДА (HX-Trigger)
    document.body.addEventListener('showMessage', function (evt) {
        const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
        if (messageText) {
            const container = document.querySelector('.messages-container') || createMessagesContainer();
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success';
            alertDiv.innerHTML = `<span>${messageText}</span>`;
            container.appendChild(alertDiv);
            autoDismissAlerts();
        }
    });

    function createMessagesContainer() {
        const cont = document.createElement('div');
        cont.className = 'messages-container';
        document.querySelector('.div-box-storage-acceptable').insertBefore(cont, formContainer);
        return cont;
    }
});