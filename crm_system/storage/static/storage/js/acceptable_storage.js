document.addEventListener('DOMContentLoaded', function () {
    const addFormBtn = document.getElementById('add-new-form-acceptable');
    const formsList = document.getElementById('acceptable-div-form');

    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    const emptyFormTemplate = document.getElementById('empty-form-acceptable').innerHTML;

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

            // Инициализация Select2 для нового селекта с задержкой
            setTimeout(function () {
                const $lastRow = $('#acceptable-div-form tr.item-row:last-child');
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
});

// 3. ОБРАБОТЧИК СООБЩЕНИЙ ОТ БЭКЕНДА (HX-Trigger)
document.body.addEventListener('showMessage', function (evt) {
    const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
    if (messageText) alert(messageText);
});

// 4. ЗАЩИТА ОТ ДУРАКОВ (Количество не может быть меньше 1)
document.addEventListener('input', function (e) {
    if (!document.getElementById('acceptable-div-form')) return;

    if (e.target && e.target.name && (e.target.name.includes('quantity_at_the_purchase') || e.target.name.includes('minimum_items_for_notification'))) {
        let val = parseFloat(e.target.value);
        if (e.target.value === '') return;
        if (val < 1) {
            e.target.value = 1;
        }
    }
});