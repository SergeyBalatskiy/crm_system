// ==============================================================================
// 1. ВСПOМОГАТЕЛЬНЫЕ ФУНКЦИИ И ИНИЦИАЛИЗАЦИЯ SELECT2
// ==============================================================================

function formatThousands(value) {
    let numbers = String(value).replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

function initRowSelect2($row) {
    const $sel = $row.find('select');
    if (!$sel.length) return;

    if ($sel.data('select2')) {
        $sel.select2('destroy');
    }

    $sel.removeAttr('data-select2-id')
        .removeClass('select2-hidden-accessible')
        .show();

    $sel.select2({
        ajax: {
            url: $sel.attr('data-autocomplete-light-url') || '/storage/storage-autocomplete',
            dataType: 'json',
            delay: 250,
            data: function (params) { return { q: params.term }; },
            processResults: function (data) { return { results: data.results || data }; },
            cache: true
        },
        placeholder: $sel.attr('data-placeholder') || 'Начните вводить название, код или поставщика',
        allowClear: true,
        width: '100%'
    });
}

function reindexRemovalForms() {
    const container = document.getElementById('removal-div-form');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]') || document.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!container || !totalFormsInput) return;

    const rows = container.querySelectorAll('tr.item-row');
    totalFormsInput.value = rows.length;

    rows.forEach((row, index) => {
        const $row = $(row);

        row.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.name) input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
            if (input.id) input.id = input.id.replace(/id_form-\d+-/, `id_form-${index}-`);
        });

        const $select = $row.find('select');
        if ($select.length && !$select.data('select2')) {
            initRowSelect2($row);
        }
    });
}

// ==============================================================================
// 2. ФУНКЦИИ ДОБАВЛЕНИЯ И УДАЛЕНИЯ (ВЫЗЫВАЮТСЯ ИЗ HTML ЧЕРЕЗ ONCLICK)
// ==============================================================================

function addRemovalRow() {
    const container = document.getElementById('removal-div-form');
    const template = document.getElementById('removal-row-template');
    if (!container || !template) return;

    const currentCount = container.querySelectorAll('tr.item-row').length;
    const templateContent = template.innerHTML || template.textContent;

    const newFormHtml = templateContent.replace(/__prefix__/g, currentCount);
    container.insertAdjacentHTML('beforeend', newFormHtml);

    reindexRemovalForms();
}

function removeRemovalRow(btnElement) {
    const container = document.getElementById('removal-div-form');
    if (!container) return;

    const rows = container.querySelectorAll('tr.item-row');
    if (rows.length > 1) {
        const $row = $(btnElement).closest('tr.item-row');
        const $select = $row.find('select');

        if ($select.length && $select.data('select2')) {
            $select.select2('destroy');
        }

        $row.remove();
        reindexRemovalForms();
    }
}

// Инициализация существующих элементов при первой загрузке
$(document).ready(function () {
    const $container = $('#removal-div-form');
    if ($container.length) {
        reindexRemovalForms();
    }
});

// ==============================================================================
// 3. ЗАЩИТА И ФОРМАТИРОВАНИЕ ПОЛЯ КОЛИЧЕСТВА
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

document.addEventListener('blur', function (e) {
    if (!document.getElementById('removal-div-form')) return;

    if (e.target && e.target.name && e.target.name.includes('quantity_history')) {
        if (e.target.value === '' || parseInt(e.target.value.replace(/\D/g, ''), 10) < 1) {
            e.target.value = 1;
        }
    }
}, true);

// ==============================================================================
// 4. РАБОТА С SELECT2 (АВТОЗАПОЛНЕНИЕ, ОЧИСТКА И ФОРМАТИРОВАНИЕ)
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

$(document).on('select2:clear select2:unselect', 'select[data-autocomplete-light-function]', function (e) {
    if (!$(this).closest('#removal-div-form').length) return;
    const $formRow = $(this).closest('.django-form');

    $formRow.find('input[name$="-individual_code_history"]').val('');
    $formRow.find('.stock-remainder-input').val('');
    $formRow.find('input[name$="-supplier_history"]').val('');
    $formRow.find('input[name$="-quantity_history"]').val('1');
});

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

// ==============================================================================
// 5. HTMX И ОТПРАВКА ФОРМЫ
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

document.body.addEventListener('showMessage', function (evt) {
    const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
    if (messageText) alert(messageText);
});