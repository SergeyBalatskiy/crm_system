// Глобальная функция закрытия тоастов
function dismissAlert(alertEl) {
    if (!alertEl || alertEl.classList.contains('fade-out')) return;
    alertEl.classList.add('fade-out');
    setTimeout(() => alertEl.remove(), 300);
}

$(document).ready(function () {
    const getCsrfToken = () => $('[name=csrfmiddlewaretoken]').val();

    // ----------------------------------------------------
    // 1. Форматирование цен (пробелы каждые 3 цифры)
    // ----------------------------------------------------
    $(document).on('input', '.price-format-input', function () {
        let rawValue = $(this).val().replace(/\D/g, '');

        if (rawValue) {
            let formattedValue = rawValue.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
            $(this).val(formattedValue);
        } else {
            $(this).val('');
        }
    });

    // ----------------------------------------------------
    // 2. Отрисовка пунктов Select2 с крестиком удаления
    // ----------------------------------------------------
    function formatCategoryOption(option) {
        if (!option.id) {
            return option.text;
        }

        const $container = $(`
            <div class="select2-category-item">
                <span class="select2-category-title">${option.text}</span>
                <button type="button" class="select2-category-delete-btn" title="Удалить категорию">&times;</button>
            </div>
        `);

        const $deleteBtn = $container.find('.select2-category-delete-btn');

        // Блокируем выбор элемента при клике на крестик
        $deleteBtn.on('mousedown mouseup', function (e) {
            e.stopPropagation();
        });

        $deleteBtn.on('click', function (e) {
            e.stopPropagation();
            e.preventDefault();

            const categoryName = option.text;
            const confirmDelete = confirm(`Вы действительно хотите удалить категорию «${categoryName}» и ВСЕ связанные с ней услуги?`);

            if (confirmDelete) {
                const deleteUrl = typeof DELETE_SERVICES_URL !== 'undefined' ? DELETE_SERVICES_URL : '/services/delete';

                htmx.ajax('POST', deleteUrl, {
                    values: {
                        'category': categoryName,
                        'csrfmiddlewaretoken': getCsrfToken()
                    }
                });
            }
        });

        return $container;
    }

    // Единственная инициализация Select2
    $('.select2-creatable').select2({
        tags: true,
        placeholder: "Выберите или введите категорию",
        allowClear: true,
        width: '100%',
        templateResult: formatCategoryOption
    });

    // ----------------------------------------------------
    // 3. Обработка HTMX Toast-уведомлений
    // ----------------------------------------------------
    document.body.addEventListener('showToast', function (evt) {
        const data = evt.detail;
        if (data) {
            createToast(data.message, data.level || 'error');
        }
    });

    function createToast(message, level) {
        let container = document.getElementById('messages-wrapper');

        if (!container) {
            container = document.createElement('div');
            container.className = 'messages-wrapper';
            container.id = 'messages-wrapper';
            document.body.appendChild(container);
        }

        container.innerHTML = '';

        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${level}`;

        let iconSvg = '';
        if (level === 'success') {
            iconSvg = `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l4.992-5.99a.75.75 0 0 0-.018-1.042z"/>
            </svg>`;
        } else if (level === 'error' || level === 'danger') {
            iconSvg = `<svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
            </svg>`;
        }

        alertEl.innerHTML = `
            ${iconSvg}
            <span class="alert-text">${message}</span>
            <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
        `;

        container.appendChild(alertEl);

        setTimeout(() => {
            dismissAlert(alertEl);
        }, 4000);
    }
});