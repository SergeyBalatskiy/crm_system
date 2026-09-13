// 1. Настройка Select2: отображение только имени в выбранном поле
if (window.jQuery && window.jQuery.fn.select2) {
    window.jQuery.fn.select2.defaults.set('templateSelection', function (item) {
        if (!item.id) {
            return item.text;
        }
        if (item.name) {
            return item.name;
        }
        if (item.text && item.text.includes('|')) {
            return item.text.split('|')[0].trim();
        }
        return item.text;
    });
}

// 2. Добавление и удаление строк в таблице
document.addEventListener('click', function (e) {
    // Добавление новой строки
    if (e.target && (e.target.id === 'add-new-form-removal' || e.target.closest('#add-new-form-removal'))) {
        const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
        const emptyFormContainer = document.getElementById('empty-form-removal');
        const formsList = document.getElementById('removal-div-form');

        if (totalFormsInput && emptyFormContainer && formsList) {
            let currentFormCount = parseInt(totalFormsInput.value);
            let newFormHtml = emptyFormContainer.innerHTML.replace(/__prefix__/g, currentFormCount);

            const tempTbody = document.createElement('tbody');
            tempTbody.innerHTML = newFormHtml;

            // Очищаем Select2 атрибуты для корректной инициализации нового поля
            tempTbody.querySelectorAll('.select2-container').forEach(el => el.remove());
            tempTbody.querySelectorAll('select').forEach(select => {
                select.removeAttribute('data-select2-id');
                select.classList.remove('select2-hidden-accessible');
                select.style.display = '';
            });

            // Нумерация строк
            const visualRowIndex = formsList.querySelectorAll('tr').length + 1;
            const rowNumberCell = tempTbody.querySelector('.row-number .hash');
            if (rowNumberCell) {
                rowNumberCell.textContent = visualRowIndex;
            }

            formsList.appendChild(tempTbody.firstElementChild);
            totalFormsInput.value = currentFormCount + 1;

            // Переинициализация django-autocomplete-light
            if (window.jQuery) {
                window.jQuery(document).trigger('dal-init-function');
            }
        }
    }

    // Удаление строки по кнопке-крестику
    if (e.target && e.target.classList.contains('btn-remove-row')) {
        const row = e.target.closest('tr');
        const formsList = document.getElementById('removal-div-form');

        if (row && formsList.querySelectorAll('tr').length > 1) {
            row.remove();
            formsList.querySelectorAll('tr').forEach((tr, index) => {
                const numCell = tr.querySelector('.row-number .hash');
                if (numCell) numCell.textContent = index + 1;
            });
        }
    }
});

// 3. Блокировка выпадающего списка при клике на крестик сброса
$(document).on('select2:unselecting', 'select[data-autocomplete-light-function]', function (e) {
    $(this).data('unselecting', true);
});

$(document).on('select2:opening', 'select[data-autocomplete-light-function]', function (e) {
    if ($(this).data('unselecting')) {
        $(this).removeData('unselecting');
        e.preventDefault();
    }
});

// 4. Очистка смежных полей при сбросе выбора
$(document).on('select2:clear select2:unselect', 'select[data-autocomplete-light-function]', function (e) {
    const $formRow = $(this).closest('.django-form');

    $formRow.find('input[name$="-individual_code_history"]').val('');
    $formRow.find('.stock-remainder-input').val('');
    $formRow.find('input[name$="-supplier_history"]').val('');
    $formRow.find('input[name$="-quantity_history"]').val('1');
});

// 5. Автозаполнение смежных полей при выборе товара
$(document).on('select2:select', 'select[data-autocomplete-light-function]', function (e) {
    const data = e.params.data;
    const $select = $(this);
    const $formRow = $select.closest('.django-form');

    if (data.code !== undefined) {
        $formRow.find('input[name$="-individual_code_history"]').val(data.code);
    }

    if (data.remainder !== undefined) {
        $formRow.find('.stock-remainder-input').val(data.remainder);
    }

    if (data.supplier !== undefined) {
        $formRow.find('input[name$="-supplier_history"]').val(data.supplier);
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

// 6. Форматирование тысяч
function formatThousands(value) {
    let numbers = String(value).replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// 7. Форматирование поля количества при ручном вводе
document.addEventListener('input', function (e) {
    if (e.target.matches('input[name$="-quantity_history"]')) {
        if (e.target.type === 'number') {
            e.target.type = 'text';
        }
        let cursorPosition = e.target.selectionStart;
        let oldLength = e.target.value.length;
        e.target.value = formatThousands(e.target.value);
        let newLength = e.target.value.length;
        cursorPosition = cursorPosition + (newLength - oldLength);
        e.target.setSelectionRange(cursorPosition, cursorPosition);
    }
});

// 8. Очистка пробелов перед отправкой HTMX / Form submit
document.body.addEventListener('htmx:configRequest', function (evt) {
    let params = evt.detail.parameters;
    for (let key in params) {
        if (key.includes('-quantity_history')) {
            params[key] = String(params[key]).replace(/\s/g, '');
        }
    }
});

document.addEventListener('submit', function (e) {
    let inputs = e.target.querySelectorAll('input[name$="-quantity_history"]');
    inputs.forEach(input => {
        input.value = input.value.replace(/\s/g, '');
    });
});

// 9. Уведомления HX-Trigger
document.body.addEventListener('showMessage', function (evt) {
    const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
    if (messageText) {
        alert(messageText);
    }
});
