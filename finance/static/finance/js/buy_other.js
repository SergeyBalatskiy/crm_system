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


function dismissAlert(alertEl) {
    if (!alertEl || alertEl.classList.contains('fade-out')) return;
    alertEl.classList.add('fade-out');
    setTimeout(() => alertEl.remove(), 300);
}

// 2. Таймер автозакрытия через 4 секунды
function autoDismiss(alertEl) {
    setTimeout(() => dismissAlert(alertEl), 4000);
}

// Инициализация при стандартной загрузке Django-сообщений
document.querySelectorAll('.messages-wrapper .alert').forEach(autoDismiss);

// 3. Динамическое создание плашки для HTMX событии showToast
function renderHtmxToast(level, message) {
    let wrapper = document.querySelector('.messages-wrapper');

    // Если обёртки нет — создаем её на лету
    if (!wrapper) {
        wrapper = document.createElement('div');
        wrapper.className = 'messages-wrapper';
        document.body.appendChild(wrapper);
    }

    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${level}`;

    const isSuccess = level === 'success';
    const iconSvg = isSuccess
        ? `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l4.992-5.99a.75.75 0 0 0-.018-1.042z"/></svg>`
        : `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>`;

    alertEl.innerHTML = `
            ${iconSvg}
            <span class="alert-text">${message}</span>
            <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
        `;

    wrapper.appendChild(alertEl);
    autoDismiss(alertEl);
}

// 4. Слушатель события showToast, вызванного заголовком HX-Trigger из Django
document.body.addEventListener('showToast', function (evt) {
    if (evt.detail) {
        const level = evt.detail.level || 'error';
        const message = evt.detail.message || '';
        renderHtmxToast(level, message);
    }
});

function renderHtmxToast(level, message) {
    let wrapper = document.querySelector('.messages-wrapper');

    // Если обёртки нет — создаем её на лету
    if (!wrapper) {
        wrapper = document.createElement('div');
        wrapper.className = 'messages-wrapper';
        document.body.appendChild(wrapper);
    } else {
        // Очищаем все предыдущие плашки, чтобы они не стакались
        wrapper.innerHTML = '';
    }

    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${level}`;

    const isSuccess = level === 'success';
    const iconSvg = isSuccess
        ? `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l4.992-5.99a.75.75 0 0 0-.018-1.042z"/></svg>`
        : `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>`;

    alertEl.innerHTML = `
        ${iconSvg}
        <span class="alert-text">${message}</span>
        <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
    `;

    wrapper.appendChild(alertEl);
    autoDismiss(alertEl);
}