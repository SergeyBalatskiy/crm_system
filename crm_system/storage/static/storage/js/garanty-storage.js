// Настройка Select2: отображение только названия в выбранном поле
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

// Добавление и удаление строк в таблице
document.addEventListener('click', function (e) {
    // Добавление новой строки
    if (e.target && (e.target.id === 'add-new-form-garanty' || e.target.closest('#add-new-form-garanty'))) {
        const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
        const emptyFormContainer = document.getElementById('empty-form-garanty');
        const formsList = document.getElementById('garanty-div-form');

        if (totalFormsInput && emptyFormContainer && formsList) {
            let currentFormCount = parseInt(totalFormsInput.value);
            let newFormHtml = emptyFormContainer.innerHTML.replace(/__prefix__/g, currentFormCount);

            const tempTbody = document.createElement('tbody');
            tempTbody.innerHTML = newFormHtml;

            // Очистка Select2 атрибутов для корректной инициализации нового поля
            tempTbody.querySelectorAll('.select2-container').forEach(el => el.remove());
            tempTbody.querySelectorAll('select').forEach(select => {
                select.removeAttribute('data-select2-id');
                select.classList.remove('select2-hidden-accessible');
                select.style.display = '';
            });

            // Расчет визуального номера строки
            const visualRowIndex = formsList.querySelectorAll('tr').length + 1;
            const rowNumberCell = tempTbody.querySelector('.row-number .hash');
            if (rowNumberCell) {
                rowNumberCell.textContent = visualRowIndex;
            }

            formsList.appendChild(tempTbody.firstElementChild);
            totalFormsInput.value = currentFormCount + 1;

            if (window.jQuery) {
                window.jQuery(document).trigger('dal-init-function');
            }
        }
    }

    // Удаление строки по кнопке-крестику
    if (e.target && e.target.classList.contains('btn-remove-row')) {
        const row = e.target.closest('tr');
        const formsList = document.getElementById('garanty-div-form');

        if (row && formsList.querySelectorAll('tr').length > 1) {
            row.remove();
            // Обновляем нумерацию оставшихся строк
            formsList.querySelectorAll('tr').forEach((tr, index) => {
                const numCell = tr.querySelector('.row-number .hash');
                if (numCell) numCell.textContent = index + 1;
            });
        }
    }
});

// Блокировка выпадающего списка при клике на крестик сброса
$(document).on('select2:unselecting', 'select[data-autocomplete-light-function]', function (e) {
    $(this).data('unselecting', true);
});

$(document).on('select2:opening', 'select[data-autocomplete-light-function]', function (e) {
    if ($(this).data('unselecting')) {
        $(this).removeData('unselecting');
        e.preventDefault();
    }
});

// Очистка смежных полей при сбросе выбора
$(document).on('select2:clear select2:unselect', 'select[data-autocomplete-light-function]', function (e) {
    const $formRow = $(this).closest('.django-form');

    $formRow.find('input[name$="-individual_code_history"]').val('');
    $formRow.find('.stock-remainder-input').val('');
    $formRow.find('input[name$="-supplier_history"]').val('');
    $formRow.find('input[name$="-buy_price_history"]').val('');
    $formRow.find('input[name$="-quantity_history"]').val('');
});

// Автозаполнение смежных полей при выборе товара
$(document).on('select2:select', 'select[data-autocomplete-light-function]', function (e) {
    const data = e.params.data;
    const $select = $(this);
    const $formRow = $select.closest('.django-form');

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

// Форматирование тысяч
function formatThousands(value) {
    let numbers = String(value).replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Автоматическое выделение всего содержимого при фокусе на количество или цену
document.addEventListener('focusin', function (e) {
    if (e.target.matches('input[name$="-buy_price_history"], input[name$="-quantity_history"]')) {
        let input = e.target;

        // Меняем тип на text сразу при входе, чтобы браузер разрешил управление курсором
        if (input.type === 'number') {
            input.type = 'text';
        }

        setTimeout(function () {
            input.select();
        }, 0);
    }
});

// Динамический ввод с сохранением позиции курсора
document.addEventListener('input', function (e) {
    if (e.target.matches('input[name$="-quantity_history"], input[name$="-buy_price_history"]')) {
        let input = e.target;

        if (input.type === 'number') {
            input.type = 'text';
        }

        let oldLength = input.value.length;
        let cursorPosition = input.selectionStart;

        // Если позицию определить не удалось, ставим курсор В КОНЕЦ (oldLength), а не в 0
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

// Очистка пробелов перед отправкой HTMX / Form submit
document.body.addEventListener('htmx:configRequest', function (evt) {
    let params = evt.detail.parameters;
    for (let key in params) {
        if (key.includes('-buy_price_history') || key.includes('-quantity_history')) {
            params[key] = String(params[key]).replace(/\s/g, '');
        }
    }
});

document.addEventListener('submit', function (e) {
    let inputs = e.target.querySelectorAll('input[name$="-buy_price_history"], input[name$="-quantity_history"]');
    inputs.forEach(input => {
        input.value = input.value.replace(/\s/g, '');
    });
});

// Уведомления HX-Trigger
document.body.addEventListener('showMessage', function (evt) {
    const messageText = typeof evt.detail === 'object' && evt.detail !== null ? evt.detail.value : evt.detail;
    if (messageText) {
        alert(messageText);
    }
});

// Проверка минимального значения при завершении ввода (при уходе из поля)
document.addEventListener('change', function (e) {
    if (e.target.matches('input[name$="-quantity_history"]')) {
        let val = parseInt(e.target.value.replace(/\s/g, ''), 10);

        // Если ввели 0, отрицательное число или пустоту — сбрасываем на 1
        if (isNaN(val) || val < 1) {
            e.target.value = '1';
        }
    }
});