console.log('🚀 [Finance Sell Items] Модуль продажи успешно инициализирован');

// ==============================================================================
// 1. ИЗВЛЕЧЕНИЕ ЧИСТОГО ИМЕНИ ТОВАРА И НАСТРОЙКА SELECT2
// ==============================================================================
function extractProductName(item) {
    if (!item || !item.id) return item.text || '';

    if (item.name) return item.name;

    if (item.element && $(item.element).data('name')) {
        return $(item.element).data('name');
    }

    let text = (item.text || '').trim();

    let match = text.match(/Товар:\s*([^|]+)/i);
    if (match && match[1] && match[1].trim()) {
        return match[1].trim();
    }

    if (text.includes('|')) {
        let parts = text.split('|');
        let namePart = parts.find(p => !p.toLowerCase().includes('код:') && !p.toLowerCase().includes('поставщик:'));
        if (namePart) return namePart.replace(/Товар:\s*/i, '').trim();
    }

    return text.replace(/Код:\s*\d+/gi, '').trim() || text;
}

function formatDropdownResult(item) {
    if (!item.id) return item.text;
    return item.text;
}

if (window.jQuery && window.jQuery.fn.select2) {
    $.fn.select2.defaults.set('templateSelection', extractProductName);
    $.fn.select2.defaults.set('templateResult', formatDropdownResult);
}

// ==============================================================================
// 2. ИНИЦИАЛИЗАЦИЯ SELECT2 ДЛЯ ПРОДАЖИ
// ==============================================================================
function initCustomSelect2($context) {
    $context.find('select').each(function () {
        const $sel = $(this);

        if ($sel.hasClass('select2-hidden-accessible') || $sel.data('select2')) {
            $sel.select2('destroy');
        }

        const autocompleteUrl = $sel.attr('data-autocomplete-light-url') || '/finance/finance-autocomplete';

        $sel.select2({
            ajax: {
                url: autocompleteUrl,
                dataType: 'json',
                delay: 250,
                data: params => ({ q: params.term }),
                processResults: data => ({ results: data.results || data }),
                cache: true
            },
            placeholder: $sel.attr('data-placeholder') || 'Начните вводить название, код или поставщика',
            allowClear: true,
            width: '100%',
            templateSelection: extractProductName,
            templateResult: formatDropdownResult
        });

        // Восстановление названия и остатка, если форма вернулась с ошибкой и у поля уже есть значение
        const selectedVal = $sel.val();
        if (selectedVal) {
            const $row = $sel.closest('tr.item-row');

            $.ajax({
                url: autocompleteUrl,
                dataType: 'json',
                data: { q: selectedVal }
            }).done(function (data) {
                const results = data.results || data;
                if (!results || !results.length) return;

                // Ищем элемент, соответствующий выбранному ID
                const item = results.find(i => String(i.id) === String(selectedVal)) || results[0];
                if (item) {
                    const cleanName = extractProductName(item);

                    // 1. Обновляем текст в <option> и атрибуты для корректного отображения имени
                    let $option = $sel.find('option:selected');
                    if ($option.length) {
                        $option.text(cleanName).attr('data-name', cleanName).data('name', cleanName);
                    } else {
                        $option = new Option(cleanName, item.id, true, true);
                        $sel.append($option);
                    }
                    $sel.trigger('change.select2');

                    // 2. Восстанавливаем значение в поле "Остаток"
                    if (item.remainder !== undefined && item.remainder !== null) {
                        $row.find('.stock-remainder-input').val(item.remainder);
                    }
                }
            });
        }
    });
}

// ==============================================================================
// 3. УПРАВЛЕНИЕ ФОРМСЕТОМ (ДОБАВЛЕНИЕ / УДАЛЕНИЕ / ПЕРЕИНДЕКСАЦИЯ)
// ==============================================================================
function reindexFormset(container) {
    if (!container) return;

    const $container = $(container);

    // 1. Уничтожаем Select2 на всех элементах таблицы перед изменением ID
    $container.find('select').each(function () {
        if ($(this).data('select2')) {
            $(this).select2('destroy');
        }
    });

    const rows = container.querySelectorAll('tr.item-row');
    const form = container.closest('form');
    const totalFormsInput = form
        ? form.querySelector('input[name$="-TOTAL_FORMS"]')
        : document.querySelector('input[name$="-TOTAL_FORMS"]');

    if (totalFormsInput) {
        totalFormsInput.value = rows.length;
    }

    // 2. Обновляем name и id у всех полей
    rows.forEach((row, index) => {
        row.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.name) input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
            if (input.id) input.id = input.id.replace(/id_form-\d+-/, `id_form-${index}-`);
        });
    });

    // 3. Заново инициализируем Select2 для обновленных строк
    initCustomSelect2($container);
}

function addFormRow(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);
    if (!container || !template) return;

    const currentCount = container.querySelectorAll('tr.item-row').length;
    let html = (template.innerHTML || template.textContent).replace(/__prefix__/g, currentCount);

    const tempTbody = document.createElement('tbody');
    tempTbody.innerHTML = html;

    tempTbody.querySelectorAll('.select2-container').forEach(el => el.remove());
    tempTbody.querySelectorAll('select').forEach(select => {
        select.removeAttribute('data-select2-id');
        select.classList.remove('select2-hidden-accessible');
        select.style.display = '';
    });

    const newRow = tempTbody.querySelector('tr.item-row') || tempTbody.firstElementChild;
    container.appendChild(newRow);

    reindexFormset(container);
}

function removeFormRow(btn) {
    const row = btn.closest('tr.item-row');
    if (!row) return;

    const container = row.closest('tbody');
    if (!container) return;

    const rows = container.querySelectorAll('tr.item-row');
    if (rows.length > 1) {
        row.remove();
        reindexFormset(container);
    }
}

// Глобальные функции для работы с onclick="addSellRow()" и onclick="SellRemovalRow(this)"
window.addSellRow = function () {
    addFormRow('sell-div-form', 'sell-row-template');
};

window.SellRemovalRow = function (btn) {
    removeFormRow(btn);
};

// ==============================================================================
// 4. СОБЫТИЯ И ИНИЦИАЛИЗАЦИЯ
// ==============================================================================
$(document).on('autocompleteLight:initialised', function (e, $element) {
    initCustomSelect2($element.parent());
});

$(document).ready(function () {
    const $container = $('#sell-div-form');
    if ($container.length) {
        initCustomSelect2($container);
    }
});

// ==============================================================================
// 5. АВТОЗАПОЛНЕНИЕ ПОЛЕЙ СТРОКИ ПРИ ВЫБОРЕ ТОВАРА
// ==============================================================================
$(document).on('select2:select', 'select', function (e) {
    const $container = $(this).closest('#sell-div-form');
    if (!$container.length) return;

    const data = e.params.data;
    const $row = $(this).closest('tr.item-row');

    if (data.code !== undefined) $row.find('input[name$="-individual_code_history"]').val(data.code);
    if (data.remainder !== undefined) $row.find('.stock-remainder-input').val(data.remainder);
    if (data.supplier !== undefined) $row.find('input[name$="-supplier_history"]').val(data.supplier);

    // --- ДОБАВЛЕНО: Вставка цены продажи ---
    if (data.price !== undefined && data.price !== null) {
        let priceNum = Math.round(parseFloat(data.price) || 0);
        const $priceInput = $row.find('input[name$="-buy_price_history"]');
        if ($priceInput.length) {
            if ($priceInput.attr('type') === 'number') {
                $priceInput.attr('type', 'text');
            }
            $priceInput.val(formatThousands(priceNum));
        }
    }
    // ----------------------------------------

    const cleanName = extractProductName(data);
    const $option = $(this).find('option:selected');
    $option.attr('data-name', cleanName).data('name', cleanName);
});

// Подрезка отображения длинных названий после выбора в Select2
$(document).on('select2:select change', 'select', function () {
    const $select = $(this);
    setTimeout(() => {
        const $rendered = $select.next('.select2-container').find('.select2-selection__rendered');
        if (!$rendered.length) return;

        let fullText = $rendered.text();
        let match = fullText.match(/Товар:\s*([^|]+)/i);
        if (match && match[1]) {
            const cleanName = match[1].trim();
            const $clearBtn = $rendered.find('.select2-selection__clear');

            $rendered.text(cleanName);
            if ($clearBtn.length) {
                $rendered.prepend($clearBtn);
            }
        }
    }, 10);
});

// ДОБАВЛЕНО: Очистка полей строки при клике на крестик удаления (сброс)
$(document).on('select2:unselect select2:clear', 'select', function (e) {
    const $row = $(this).closest('tr.item-row');
    if (!$row.length) return;

    $row.find('input[name$="-individual_code_history"]').val('');
    $row.find('.stock-remainder-input').val('');
    $row.find('input[name$="-supplier_history"]').val('');
    $row.find('input[name$="-buy_price_history"]').val('');
    $row.find('input[name$="-quantity_history"]').val('1');
});
// ==============================================================================
// 6. ФОРМАТИРОВАНИЕ И САНИТИЗАЦИЯ ВВОДА (ЦЕНА И КОЛИЧЕСТВО)
// ==============================================================================
function formatThousands(value) {
    return String(value).replace(/\D/g, '').replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

document.addEventListener('focusin', function (e) {
    if (e.target.matches('input[name$="-quantity_history"], input[name$="-buy_price_history"]')) {
        if (e.target.type === 'number') e.target.type = 'text';
        setTimeout(() => e.target.select(), 0);
    }
});

document.addEventListener('input', function (e) {
    if (e.target.matches('input[name$="-quantity_history"], input[name$="-buy_price_history"]')) {
        let input = e.target;
        if (input.type === 'number') input.type = 'text';

        let oldLength = input.value.length;
        let cursorPosition = input.selectionStart ?? oldLength;

        input.value = formatThousands(input.value);
        let newLength = input.value.length;
        let newCursorPosition = Math.max(0, Math.min(cursorPosition + (newLength - oldLength), newLength));

        input.setSelectionRange(newCursorPosition, newCursorPosition);
    }
});

document.addEventListener('change', function (e) {
    if (e.target.matches('input[name$="-quantity_history"]')) {
        let val = parseInt(e.target.value.replace(/\D/g, ''), 10);
        if (isNaN(val) || val < 1) e.target.value = '1';
    }
});

function sanitizeFormInputs(form) {
    if (!form) return;
    form.querySelectorAll('input[name$="-quantity_history"], input[name$="-buy_price_history"]').forEach(input => {
        input.value = input.value.replace(/\D/g, '');
    });
}

document.addEventListener('submit', e => sanitizeFormInputs(e.target));

document.body.addEventListener('htmx:configRequest', function (evt) {
    const params = evt.detail.parameters;
    for (let key in params) {
        if (key.includes('-quantity_history') || key.includes('-buy_price_history')) {
            params[key] = String(params[key]).replace(/\D/g, '');
        }
    }

    const form = evt.detail.elt.closest('form');
    if (form) {
        form.querySelectorAll('input[name$="-quantity_history"], input[name$="-buy_price_history"]').forEach(input => {
            input.value = input.value.replace(/\D/g, '');
        });
    }
});

document.body.addEventListener('htmx:afterSettle', function (evt) {
    const $container = $('#sell-div-form');
    if ($container.length) {
        initCustomSelect2($container);
    }
});

// Функция для динамического создания красивого плавающего алерта
function createAlert(message, level = 'error') {
    let wrapper = document.querySelector('.messages-wrapper');

    // Если контейнера на странице нет, создаем его динамически
    if (!wrapper) {
        wrapper = document.createElement('div');
        wrapper.className = 'messages-wrapper';
        document.body.appendChild(wrapper);
    }

    // 🔥 ОЧИЩАЕМ СТАРЫЕ СООБЩЕНИЯ (чтобы они не строились в столбик)
    wrapper.innerHTML = '';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${level}`;

    let iconSvg = '';
    if (level === 'success') {
        iconSvg = `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l4.992-5.99a.75.75 0 0 0-.018-1.042z"/></svg>`;
    } else if (level === 'error' || level === 'danger') {
        iconSvg = `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>`;
    }

    alertDiv.innerHTML = `
        ${iconSvg}
        <span class="alert-text">${message}</span>
        <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
    `;

    wrapper.appendChild(alertDiv);

    // Автоматическое удаление через 4 секунды
    setTimeout(() => {
        dismissAlert(alertDiv);
    }, 4000);
}

// При получении события HX-Trigger 'showToast' вызываем создание сообщения
document.body.addEventListener('showToast', function (evt) {
    const detail = evt.detail; // { level: 'error', message: '...' }
    if (detail && detail.message) {
        createAlert(detail.message, detail.level || 'error');
    }
});