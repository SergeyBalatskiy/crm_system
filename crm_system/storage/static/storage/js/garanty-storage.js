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
    const rows = document.querySelectorAll('#garanty-div-form tr.item-row');
    rows.forEach((row, index) => {
        const numCell = row.querySelector('.row-number .hash');
        if (numCell) numCell.textContent = index + 1;
    });
}

// Переиндексация name/id (вызывается ТОЛЬКО при физическом удалении строки или очистке)
function reindexGarantyForms() {
    const formsList = document.getElementById('garanty-div-form');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    if (!formsList || !totalFormsInput) return;

    const rows = formsList.querySelectorAll('tr.item-row');
    totalFormsInput.value = rows.length;

    rows.forEach((row, index) => {
        row.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.name) {
                input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
            }
            if (input.id) {
                input.id = input.id.replace(/id_form-\d+-/, `id_form-${index}-`);
            }
        });
    });

    updateRowNumbers();
}

// Удаление невыбранных пустых строк перед отправкой на сервер
function cleanupEmptyRows() {
    const formsList = document.getElementById('garanty-div-form');
    if (!formsList) return;

    const rows = formsList.querySelectorAll('tr.item-row');
    rows.forEach(row => {
        const codeInput = row.querySelector('input[name$="-individual_code_history"]');
        const hasProduct = codeInput && codeInput.value.trim() !== '';

        if (!hasProduct && formsList.querySelectorAll('tr.item-row').length > 1) {
            // Разрушаем select2 перед удалением DOM node
            const $select = $(row).find('select[data-autocomplete-light-function]');
            if ($select.length && $select.data('select2')) {
                $select.select2('destroy');
            }
            row.remove();
        }
    });

    reindexGarantyForms();
}

// Форматирование разделителей тысяч (10 000)
function formatThousands(value) {
    let numbers = String(value).replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Защита от дураков: не даем ввести 0 или отрицательное число в количестве и ценах
document.addEventListener('input', function (e) {
    if (e.target && (e.target.name && e.target.name.includes('quantity_history') || e.target.name.includes('buy_price_history'))) {
        let val = parseFloat(e.target.value);

        // Если поле пустое, не трогаем (чтобы человек мог стереть и написать заново)
        if (e.target.value === '') return;

        // Для количества минимальное значение всегда 1
        if (e.target.name.includes('quantity_history')) {
            if (val < 1) {
                e.target.value = 1;
            }
        }
        // Для цены минимальное значение 0 (или больше)
        else if (e.target.name.includes('buy_price_history')) {
            if (val < 0) {
                e.target.value = 0;
            }
        }
    }
});

// Дополнительно проверяем при уходе из поля (blur), если оставили пустым или нулем
document.addEventListener('blur', function (e) {
    if (e.target && e.target.name && e.target.name.includes('quantity_history')) {
        if (e.target.value === '' || parseInt(e.target.value, 10) < 1) {
            e.target.value = 1;
        }
    }
}, true);

// ==============================================================================
// 3. ДОБАВЛЕНИЕ И ФИЗИЧЕСКОЕ УДАЛЕНИЕ СТРОК
// ==============================================================================

document.addEventListener('click', function (e) {
    const formsList = document.getElementById('garanty-div-form');
    if (!formsList) return;

    // --- 1. ДОБАВЛЕНИЕ СТРОКИ ---
    if (e.target && (e.target.id === 'add-new-form-garanty' || e.target.closest('#add-new-form-garanty'))) {
        const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
        const template = document.getElementById('empty-form-template');

        if (totalFormsInput && template) {
            let nextIndex = parseInt(totalFormsInput.value, 10) || formsList.querySelectorAll('tr.item-row').length;

            let newFormHtml = template.innerHTML.replace(/__prefix__/g, nextIndex);
            formsList.insertAdjacentHTML('beforeend', newFormHtml);

            totalFormsInput.value = nextIndex + 1;
            updateRowNumbers();

            // Даем браузеру долю секунды на рендеринг строки, чтобы у нее появилась ширина
            setTimeout(function () {
                const $lastRow = $('#garanty-div-form tr.item-row:last-child');
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
            }, 100); // 100 миллисекунд гарантируют, что браузер уже отрисовал ряд
        }
    }

    // --- 2. УДАЛЕНИЕ СТРОКИ ---
    if (e.target && e.target.classList.contains('btn-remove-row')) {
        const row = e.target.closest('tr');
        const rows = formsList.querySelectorAll('tr.item-row');

        if (row && rows.length > 1) {
            const $select = $(row).find('select');
            if ($select.length && $select.data('select2')) {
                $select.select2('destroy');
            }

            row.remove();
            reindexGarantyForms();
            updateRowNumbers();
        }
    }
});

// ==============================================================================
// 4. БЛОКИРОВКА ВЫПАДАЮЩЕГО СПИСКА ПРИ КЛИКЕ НА КРЕСТИК СБРОСА
// ==============================================================================
$(document).on('select2:unselecting', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#garanty-div-form').length) return;
    $(this).data('unselecting', true);
});

$(document).on('select2:opening', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#garanty-div-form').length) return;
    if ($(this).data('unselecting')) {
        $(this).removeData('unselecting');
        e.preventDefault();
    }
});

// ==============================================================================
// 5. ОЧИСТКА И АВТОЗАПОЛНЕНИЕ СМЕЖНЫХ ПОЛЕЙ
// ==============================================================================

// Очистка смежных полей при сбросе выбора
$(document).on('select2:clear select2:unselect', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#garanty-div-form').length) return;
    const $formRow = $(this).closest('.django-form');

    $formRow.find('input[name$="-individual_code_history"]').val('');
    $formRow.find('.stock-remainder-input').val('');
    $formRow.find('input[name$="-supplier_history"]').val('');
    $formRow.find('input[name$="-buy_price_history"]').val('');
    $formRow.find('input[name$="-quantity_history"]').val('1');
});

// Автозаполнение смежных полей при выборе товара
$(document).on('select2:select', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#garanty-div-form').length) return;
    const data = e.params.data;
    const $formRow = $(this).closest('.django-form');

    if (data.code !== undefined) {
        $formRow.find('input[name$="-individual_code_history"]').val(data.code);
    }

    if (data.remainder !== undefined) {
        $formRow.find('.stock-remainder-input').val(`${data.remainder}`);
    }

    if (data.supplier !== undefined) {
        $formRow.find('input[name$="-supplier_history"]').val(data.supplier);
    }

    if (data.price !== undefined) {
        const $priceInput = $formRow.find('input[name$="-buy_price_history"]');

        if ($priceInput.attr('type') === 'number') {
            $priceInput.attr('type', 'text');
        }

        $priceInput.val(formatThousands(data.price));
    }

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
// 6. ФОКУС, ДИНАМИЧЕСКИЙ ВВОД И КУРСОР
// ==============================================================================

document.addEventListener('focusin', function (e) {
    if (!document.getElementById('garanty-div-form')) return;

    if (e.target.matches('input[name$="-buy_price_history"], input[name$="-quantity_history"]')) {
        let input = e.target;

        if (input.type === 'number') {
            input.type = 'text';
        }

        setTimeout(function () {
            input.select();
        }, 0);
    }
});

document.addEventListener('input', function (e) {
    if (!document.getElementById('garanty-div-form')) return;

    if (e.target.matches('input[name$="-quantity_history"], input[name$="-buy_price_history"]')) {
        let input = e.target;

        if (input.type === 'number') {
            input.type = 'text';
        }

        let oldLength = input.value.length;
        let cursorPosition = input.selectionStart;

        if (cursorPosition === null) {
            cursorPosition = oldLength;
        }
        input.value = formatThousands(input.value);
        let newLength = input.value.length;
        let newCursorPosition = cursorPosition + (newLength - oldLength);
        newCursorPosition = Math.max(0, Math.min(newCursorPosition, newLength));

        input.setSelectionRange(newCursorPosition, newCursorPosition);
    }
});

document.addEventListener('change', function (e) {
    if (!document.getElementById('garanty-div-form')) return;

    if (e.target.matches('input[name$="-quantity_history"]')) {
        let val = parseInt(e.target.value.replace(/\D/g, ''), 10);

        if (isNaN(val) || val < 1) {
            e.target.value = '1';
        }
    }
});

// ==============================================================================
// 7. ОБРАБОТКА ОТПРАВКИ ФОРМЫ (HTMX И ОБЫЧНЫЙ SUBMIT)
// ==============================================================================

document.body.addEventListener('htmx:configRequest', function (evt) {
    const form = evt.detail.elt.closest('form') || document.querySelector('.garanty-form-storage');
    if (form && form.querySelector('#garanty-div-form')) {
        cleanupEmptyRows();

        const formData = new FormData(form);
        const newParams = {};

        for (let [key, val] of formData.entries()) {
            if (key.endsWith('-buy_price_history') || key.endsWith('-quantity_history')) {
                val = String(val).replace(/\D/g, '');
            }
            newParams[key] = val;
        }

        evt.detail.parameters = newParams;
    }
});

document.addEventListener('submit', function (e) {
    const form = e.target;
    if (form.querySelector && form.querySelector('#garanty-div-form')) {
        cleanupEmptyRows();

        let inputs = form.querySelectorAll('input[name$="-buy_price_history"], input[name$="-quantity_history"]');
        inputs.forEach(input => {
            input.value = input.value.replace(/\D/g, '');
        });
    }
});