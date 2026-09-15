// ==============================================================================
// 1. НАСТРОЙКА SELECT2 (Шаблон отображения выбранного элемента)
// ==============================================================================
if (window.jQuery && window.jQuery.fn.select2) {
    window.jQuery.fn.select2.defaults.set('templateSelection', function (item) {
        if (!item.id) return item.text;
        if (item.name) return item.name;
        if (item.text && item.text.includes('|')) return item.text.split('|')[0].trim();
        return item.text;
    });
}

// ==============================================================================
// 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ПЕРЕИНДЕКСАЦИЯ
// ==============================================================================

// Обновление нумерации столбца #
function updateRowNumbers() {
    const rows = document.querySelectorAll('#removal-div-form tr.item-row');
    rows.forEach((row, index) => {
        const numCell = row.querySelector('.row-number .hash');
        if (numCell) numCell.textContent = index + 1;
    });
}

// Вспомогательная функция для переиндексации полей формсета
function reindexRemovalForms() {
    const formsList = document.getElementById('removal-div-form');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    if (!formsList || !totalFormsInput) return;

    const rows = formsList.querySelectorAll('tr.item-row');
    totalFormsInput.value = rows.length;

    rows.forEach((row, index) => {
        row.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.name) input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
            if (input.id) input.id = input.id.replace(/id_form-\d+-/, `id_form-${index}-`);
        });
    });

    updateRowNumbers();
}

// Форматирование разделителей тысяч (10 000)
function formatThousands(value) {
    let numbers = String(value).replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// ==============================================================================
// 3. ЗАЩИТА ОТ ДУРАКОВ (КОЛИЧЕСТВО НЕ МЕНЬШЕ 1)
// ==============================================================================
document.addEventListener('input', function (e) {
    if (!document.getElementById('removal-div-form')) return;

    if (e.target && e.target.name && e.target.name.includes('quantity_history')) {
        if (e.target.type === 'number') e.target.type = 'text';

        let val = parseFloat(e.target.value);
        if (e.target.value === '') return;

        if (val < 1) {
            e.target.value = 1;
        }

        let cursorPosition = e.target.selectionStart;
        let oldLength = e.target.value.length;
        e.target.value = formatThousands(e.target.value);
        let newLength = e.target.value.length;
        cursorPosition = cursorPosition + (newLength - oldLength);
        e.target.setSelectionRange(cursorPosition, cursorPosition);
    }
});

// Проверка при уходе из поля (blur), если оставили пустым или нулем
document.addEventListener('blur', function (e) {
    if (!document.getElementById('removal-div-form')) return;

    if (e.target && e.target.name && e.target.name.includes('quantity_history')) {
        if (e.target.value === '' || parseInt(e.target.value.replace(/\D/g, ''), 10) < 1) {
            e.target.value = 1;
        }
    }
}, true);

// ==============================================================================
// 4. ДОБАВЛЕНИЕ И УДАЛЕНИЕ СТРОК В ТАБЛИЦЕ
// ==============================================================================
document.addEventListener('click', function (e) {
    const formsList = document.getElementById('removal-div-form');
    if (!formsList) return;

    // Добавление новой строки
    if (e.target && (e.target.id === 'add-new-form-removal' || e.target.closest('#add-new-form-removal'))) {
        const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
        const emptyFormContainer = document.getElementById('empty-form-removal');

        if (totalFormsInput && emptyFormContainer) {
            let nextIndex = parseInt(totalFormsInput.value, 10) || formsList.querySelectorAll('tr.item-row').length;

            let newFormHtml = emptyFormContainer.innerHTML.replace(/__prefix__/g, nextIndex);

            const tempTbody = document.createElement('tbody');
            tempTbody.innerHTML = newFormHtml;

            // Очищаем старые артефакты select2, если они были в шаблоне
            tempTbody.querySelectorAll('.select2-container').forEach(el => el.remove());
            tempTbody.querySelectorAll('select').forEach(select => {
                select.removeAttribute('data-select2-id');
                select.classList.remove('select2-hidden-accessible');
                select.style.display = '';
            });

            formsList.appendChild(tempTbody.firstElementChild);
            totalFormsInput.value = nextIndex + 1;
            updateRowNumbers();

            // Инициализация Select2 для нового селекта с задержкой (гарантирует отрисовку)
            setTimeout(function () {
                const $lastRow = $('#removal-div-form tr.item-row:last-child');
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
                        placeholder: $sel.attr('data-placeholder') || 'Начните вводить название, код или поставщика...',
                        allowClear: true,
                        width: '100%'
                    });
                }
            }, 100);
        }
    }

    // Удаление строки по кнопке-крестику
    if (e.target && e.target.classList.contains('btn-remove-row')) {
        const row = e.target.closest('tr');
        const rows = formsList.querySelectorAll('tr.item-row');

        if (row && rows.length > 1) {
            const $select = $(row).find('select');
            if ($select.length && $select.data('select2')) {
                $select.select2('destroy');
            }

            row.remove();
            reindexRemovalForms();
        }
    }
});

// ==============================================================================
// 5. БЛОКИРОВКА ВЫПАДАЮЩЕГО СПИСКА ПРИ КЛИКЕ НА КРЕСТИК СБРОСА
// ==============================================================================
$(document).on('select2:unselecting', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#removal-div-form').length) return;
    $(this).data('unselecting', true);
});

$(document).on('select2:opening', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#removal-div-form').length) return;
    if ($(this).data('unselecting')) {
        $(this).removeData('unselecting');
        e.preventDefault();
    }
});

// ==============================================================================
// 6. ОЧИСТКА СМЕЖНЫХ ПОЛЕЙ
// ==============================================================================
$(document).on('select2:clear select2:unselect', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#removal-div-form').length) return;
    const $formRow = $(this).closest('.django-form');

    $formRow.find('input[name$="-individual_code_history"]').val('');
    $formRow.find('.stock-remainder-input').val('');
    $formRow.find('input[name$="-supplier_history"]').val('');
    $formRow.find('input[name$="-quantity_history"]').val('1');
});

// ==============================================================================
// 7. АВТОЗАПОЛНЕНИЕ ПОЛЕЙ
// ==============================================================================
$(document).on('select2:select', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#removal-div-form').length) return;
    const data = e.params.data;
    const $formRow = $(this).closest('.django-form');

    if (data.code !== undefined) $formRow.find('input[name$="-individual_code_history"]').val(data.code);
    if (data.remainder !== undefined) $formRow.find('.stock-remainder-input').val(data.remainder);
    if (data.supplier !== undefined) $formRow.find('input[name$="-supplier_history"]').val(data.supplier);

    const productName = data.name || (data.text ? data.text.split('|')[0].trim() : '');

    setTimeout(function () {
        const $rendered = $formRow.find('.select2-selection__rendered');
        const $removeBtn = $rendered.find('.select2-selection__clear');

        $rendered.attr('title', productName);
        if ($removeBtn.length) {
            $rendered.empty().append($removeBtn).append(document.createTextNode(' ' + productName));
        } else {
            $rendered.text(productName);
        }
    }, 1);
});

// ==============================================================================
// 8. ОЧИСТКА ПЕРЕД ОТПРАВКОЙ (УДАЛЕНИЕ ПРОБЕЛОВ ИЗ ЧИСЕЛ)
// ==============================================================================
document.body.addEventListener('htmx:configRequest', function (evt) {
    if (!document.getElementById('removal-div-form')) return;
    let params = evt.detail.parameters;
    for (let key in params) {
        if (key.includes('-quantity_history')) {
            params[key] = String(params[key]).replace(/\s/g, '');
        }
    }
});

document.addEventListener('submit', function (e) {
    if (!document.getElementById('removal-div-form')) return;
    let inputs = e.target.querySelectorAll('input[name$="-quantity_history"]');
    inputs.forEach(input => {
        input.value = input.value.replace(/\s/g, '');
    });
});

// ==============================================================================
// 9. УВЕДОМЛЕНИЯ HX-TRIGGER
// ==============================================================================
document.body.addEventListener('showMessage', function (evt) {
    const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
    if (messageText) alert(messageText);
});