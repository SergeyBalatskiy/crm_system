function addFormsetRow(templateId, tbodyId) {
    const template = document.getElementById(templateId);
    const tbody = document.getElementById(tbodyId);
    if (!template || !tbody) return;

    // Ищем служебное поле Django management_form
    const totalFormsInput = tbody.closest('form').querySelector('input[name$="-TOTAL_FORMS"]');
    if (!totalFormsInput) return;

    const currentCount = parseInt(totalFormsInput.value, 10);
    const templateContent = template.content.cloneNode(true);

    // Подменяем __prefix__ на текущий индекс формы
    const wrapper = document.createElement('div');
    wrapper.appendChild(templateContent);
    const updatedHtml = wrapper.innerHTML.replace(/__prefix__/g, currentCount);

    tbody.insertAdjacentHTML('beforeend', updatedHtml);
    totalFormsInput.value = currentCount + 1;
}

function addBuyOtherRow() {
    addFormsetRow('buy-other-row-template', 'other-div-form');
}

function addSellOtherRow() {
    addFormsetRow('sell-other-row-template', 'other-div-form');
}

function removeOtherRow(button) {
    const row = button.closest('tr');
    if (!row) return;

    const tbody = row.parentElement;
    const form = tbody.closest('form');
    row.remove();

    // Пересчитываем кол-во форм
    const totalFormsInput = form.querySelector('input[name$="-TOTAL_FORMS"]');
    if (totalFormsInput) {
        const remainingRows = tbody.querySelectorAll('tr.item-row').length;
        totalFormsInput.value = remainingRows;
    }
}

// Автоматическое форматирование ввода чисел с пробелами
document.addEventListener('input', function (e) {
    if (e.target.matches('input[name$="-number_in_the_operation"]')) {
        const input = e.target;

        // Запоминаем текущее положение курсора и длину текста до форматирования
        const oldCursorPos = input.selectionStart;
        const oldLength = input.value.length;

        // Оставляем ТОЛЬКО цифры (любые буквы, знаки и пробелы удаляются)
        const rawValue = input.value.replace(/\D/g, '');

        if (rawValue) {
            // Форматируем число с разделителями тысяч (обычный пробел)
            const formattedValue = rawValue.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
            input.value = formattedValue;

            // Вычисляем новое положение курсора, учитывая добавление/удаление пробелов
            const newLength = formattedValue.length;
            let newCursorPos = oldCursorPos + (newLength - oldLength);

            newCursorPos = Math.max(0, newCursorPos);
            input.setSelectionRange(newCursorPos, newCursorPos);
        } else {
            input.value = '';
        }
    }
});
