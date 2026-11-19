console.log('🚀 [Storage Dynamic Forms] Модуль успешно инициализирован');

// ==============================================================================
// 1. ИЗВЛЕЧЕНИЕ ЧИСТОГО ИМЕНИ ТОВАРА (ДЛЯ ПОЛЯ ВЫБОРА)
// ==============================================================================
function extractProductName(item) {
    if (!item || !item.id) return item.text || '';

    // 1. Из явного свойства 'name' (приходит из views.py)
    if (item.name) return item.name;

    // 2. Из data-атрибута option (если было сохранено ранее)
    if (item.element && $(item.element).data('name')) {
        return $(item.element).data('name');
    }

    let text = (item.text || '').trim();

    // 3. Достаем чистое имя из паттерна "Товар: <Название>"
    let match = text.match(/Товар:\s*([^|]+)/i);
    if (match && match[1] && match[1].trim()) {
        return match[1].trim();
    }

    // 4. Разбор по разделителям "|"
    if (text.includes('|')) {
        let parts = text.split('|');
        let namePart = parts.find(p => !p.toLowerCase().includes('код:') && !p.toLowerCase().includes('поставщик:'));
        if (namePart) return namePart.replace(/Товар:\s*/i, '').trim();
    }

    // 5. Запасная очистка подстроки "Код: N"
    return text.replace(/Код:\s*\d+/gi, '').trim() || text;
}

// Отображение в выпадающем списке (полный текст с кодом и поставщиком)
function formatDropdownResult(item) {
    if (!item.id) return item.text;
    return item.text;
}

// Устанавливаем дефолты Select2 глобально
if (window.jQuery && window.jQuery.fn.select2) {
    $.fn.select2.defaults.set('templateSelection', extractProductName);
    $.fn.select2.defaults.set('templateResult', formatDropdownResult);
}

// ==============================================================================
// 2. ПРИНУДИТЕЛЬНАЯ ИНИЦИАЛИЗАЦИЯ SELECT2 (ОБХОД DAL)
// ==============================================================================
function initCustomSelect2($context) {
    $context.find('select').each(function () {
        const $sel = $(this);

        // Уничтожаем стандартный инстанс DAL, если он успел создаться
        if ($sel.hasClass('select2-hidden-accessible') || $sel.data('select2')) {
            $sel.select2('destroy');
        }

        $sel.select2({
            ajax: {
                url: $sel.attr('data-autocomplete-light-url') || '/storage/storage-autocomplete',
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
    });
}

// ==============================================================================
// 3. УПРАВЛЕНИЕ ФОРМСЕТОМ (ДОБАВЛЕНИЕ / УДАЛЕНИЕ / ПЕРЕИНДЕКСАЦИЯ)
// ==============================================================================
function reindexFormset(container) {
    if (!container) return;

    const rows = container.querySelectorAll('tr.item-row');
    const form = container.closest('form');
    const totalFormsInput = form ? form.querySelector('input[name$="-TOTAL_FORMS"]') : document.querySelector('input[name$="-TOTAL_FORMS"]');

    if (totalFormsInput) {
        totalFormsInput.value = rows.length;
    }

    rows.forEach((row, index) => {
        row.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.name) input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
            if (input.id) input.id = input.id.replace(/id_form-\d+-/, `id_form-${index}-`);
        });
    });
}

function addFormRow(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId) || document.getElementById('empty-form-template');
    if (!container || !template) return;

    const currentCount = container.querySelectorAll('tr.item-row').length;
    let html = (template.innerHTML || template.textContent).replace(/__prefix__/g, currentCount);

    const tempTbody = document.createElement('tbody');
    tempTbody.innerHTML = html;

    // Очистка Select2 артефактов из клонируемой строки
    tempTbody.querySelectorAll('.select2-container').forEach(el => el.remove());
    tempTbody.querySelectorAll('select').forEach(select => {
        select.removeAttribute('data-select2-id');
        select.classList.remove('select2-hidden-accessible');
        select.style.display = '';
    });

    const newRow = tempTbody.querySelector('tr.item-row') || tempTbody.firstElementChild;
    container.appendChild(newRow);

    reindexFormset(container);
    initCustomSelect2($(newRow));
}

function removeFormRow(btn) {
    const row = btn.closest('tr.item-row');
    if (!row) return;

    const container = row.closest('tbody');
    if (!container) return;

    const rows = container.querySelectorAll('tr.item-row');
    if (rows.length > 1) {
        const $select = $(row).find('select');
        if ($select.length && $select.data('select2')) {
            $select.select2('destroy');
        }
        row.remove();
        reindexFormset(container);
    }
}

// ==============================================================================
// 4. СВЯЗКА СОБЫТИЙ И Перехват DAL
// ==============================================================================

// Перехватываем событие инициализации автокомплита от библиотеки DAL
$(document).on('autocompleteLight:initialised', function (e, $element) {
    initCustomSelect2($element.parent());
});

// Добавление и удаление строк
document.addEventListener('click', function (e) {
    if (e.target.closest('#add-new-form-garanty')) {
        addFormRow('garanty-div-form', 'garanty-row-template');
        return;
    }

    if (e.target.closest('#add-new-form-removal')) {
        addFormRow('removal-div-form', 'removal-row-template');
        return;
    }

    if (e.target.closest('.btn-remove-row')) {
        removeFormRow(e.target.closest('.btn-remove-row'));
        return;
    }
});

// Инициализация при полной загрузке DOM
$(document).ready(function () {
    const $containers = $('#garanty-div-form, #removal-div-form');
    if ($containers.length) {
        initCustomSelect2($containers);
    }
});

// ==============================================================================
// 5. АВТОЗАПОЛНЕНИЕ ПОЛЕЙ СТРОКИ ПРИ ВЫБОРЕ ТОВАРА
// ==============================================================================
$(document).on('select2:select', 'select', function (e) {
    const $container = $(this).closest('#removal-div-form, #garanty-div-form');
    if (!$container.length) return;

    const data = e.params.data;
    const $row = $(this).closest('tr.item-row');

    if (data.code !== undefined) $row.find('input[name$="-individual_code_history"]').val(data.code);
    if (data.remainder !== undefined) $row.find('.stock-remainder-input').val(data.remainder);
    if (data.supplier !== undefined) $row.find('input[name$="-supplier_history"]').val(data.supplier);

    // Подстановка цены закупки
    if (data.price !== undefined && data.price !== null) {
        let priceNum = Math.round(parseFloat(data.price) || 0);
        if (priceNum > 0) {
            const $priceInput = $row.find('input[name$="-buy_price_history"]');
            if ($priceInput.length) {
                // Меняем тип на text, чтобы браузер не сбрасывал строку с пробелами ("1 000")
                if ($priceInput.attr('type') === 'number') {
                    $priceInput.attr('type', 'text');
                }
                $priceInput.val(formatThousands(priceNum));
            }
        }
    }

    // Сохраняем имя товара в option
    const cleanName = extractProductName(data);
    const $option = $(this).find('option:selected');
    $option.attr('data-name', cleanName).data('name', cleanName);
});

// 🔥 2. Очистка всех связанных полей строки при клике на крестик (сбросе выбора)
$(document).on('select2:clear select2:unselect', 'select', function (e) {
    const $row = $(this).closest('tr.item-row');
    if (!$row.length) return;

    // Сбрасываем значение всех инпутов текущей строки
    $row.find('input[name$="-individual_code_history"]').val('');
    $row.find('.stock-remainder-input').val('');
    $row.find('input[name$="-supplier_history"]').val('');
    $row.find('input[name$="-buy_price_history"]').val('');
    $row.find('input[name$="-quantity_history"]').val('');
});

// ==============================================================================
// 6. ФОРМАТИРОВАНИЕ ЧИСЕЛ И ЦЕН
// ==============================================================================
function formatThousands(value) {
    return String(value).replace(/\D/g, '').replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

document.addEventListener('focusin', function (e) {
    if (e.target.matches('input[name$="-buy_price_history"], input[name$="-quantity_history"]')) {
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
    form.querySelectorAll('input[name$="-buy_price_history"], input[name$="-quantity_history"]').forEach(input => {
        input.value = input.value.replace(/\D/g, '');
    });
}

document.addEventListener('submit', e => sanitizeFormInputs(e.target));

document.body.addEventListener('htmx:configRequest', function (evt) {
    const params = evt.detail.parameters;

    // 1. Очищаем параметры, которые HTMX реально отправляет на сервер
    for (let key in params) {
        if (key.includes('-buy_price_history') || key.includes('-quantity_history')) {
            params[key] = String(params[key]).replace(/\D/g, '');
        }
    }

    // 2. Обновляем визуальное отображение в DOM
    const form = evt.detail.elt.closest('form');
    if (form) {
        form.querySelectorAll('input[name$="-buy_price_history"], input[name$="-quantity_history"]').forEach(input => {
            input.value = input.value.replace(/\D/g, '');
        });
    }
});

$(document).on('select2:select change', 'select', function () {
    const $select = $(this);

    // Ждем отрисовки Select2 в DOM
    setTimeout(() => {
        const $rendered = $select.next('.select2-container').find('.select2-selection__rendered');
        if (!$rendered.length) return;

        let fullText = $rendered.text();

        // Извлекаем только имя из строки "Код: X | Товар: Название | Поставщик: Y"
        let match = fullText.match(/Товар:\s*([^|]+)/i);
        if (match && match[1]) {
            const cleanName = match[1].trim();

            // Сохраняем кнопку очистки (крестик 'x'), если она есть
            const $clearBtn = $rendered.find('.select2-selection__clear');

            $rendered.text(cleanName);
            if ($clearBtn.length) {
                $rendered.prepend($clearBtn);
            }
        }
    }, 10);
});

// ==============================================================================
// 7. ОБРАБОТКА HTMX ОШИБОК ЧЕРЕЗ 204 СТАТУС (ОДНО СООБЩЕНИЕ ЗА РАЗ)
// ==============================================================================

window.dismissAlert = function (alertEl) {
    if (!alertEl || alertEl.classList.contains('fade-out')) return;
    alertEl.classList.add('fade-out');
    setTimeout(() => alertEl.remove(), 300);
};

document.body.addEventListener('showToast', function (evt) {
    const detail = evt.detail; // { level: 'error', message: '...' }
    if (!detail || !detail.message) return;

    const container = document.getElementById('messages-container');
    if (!container) return;

    let wrapper = container.querySelector('.messages-wrapper');
    if (!wrapper) {
        wrapper = document.createElement('div');
        wrapper.className = 'messages-wrapper';
        container.appendChild(wrapper);
    }

    // 🔥 ОЧИЩАЕМ СТАРЫЕ СООБЩЕНИЯ (чтобы они не строились в столбик)
    wrapper.innerHTML = '';

    // Создаем элемент плашки ошибки
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${detail.level || 'error'}`;

    // Иконка
    const iconSvg = detail.level === 'success'
        ? `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l4.992-5.99a.75.75 0 0 0-.018-1.042z"/></svg>`
        : `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>`;

    alertEl.innerHTML = `
        ${iconSvg}
        <span class="alert-text">${detail.message}</span>
        <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
    `;

    wrapper.appendChild(alertEl);

    // Сбрасываем и запускаем 4-секундный таймер заново для нового сообщения
    setTimeout(() => dismissAlert(alertEl), 4000);
});