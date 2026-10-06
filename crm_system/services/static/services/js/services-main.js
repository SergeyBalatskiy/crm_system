// Глобальная функция закрытия (соответствует onclick из вашего HTML)
function dismissAlert(alertEl) {
    if (!alertEl || alertEl.classList.contains('fade-out')) return;
    alertEl.classList.add('fade-out');
    setTimeout(() => alertEl.remove(), 300);
}

$(document).ready(function () {
    // Инициализация Select2
    $('.select2-creatable').select2({
        tags: true,
        placeholder: "Выберите или введите категорию",
        allowClear: true,
        width: '100%'
    });

    // Слушаем кастомное событие showToast от HTMX
    document.body.addEventListener('showToast', function (evt) {
        const data = evt.detail; // { level: 'error' | 'success', message: '...' }
        if (data) {
            createToast(data.message, data.level || 'error');
        }
    });

    function createToast(message, level) {
        let container = document.getElementById('messages-wrapper');

        // Если контейнера случайно нет на странице — создадим его
        if (!container) {
            container = document.createElement('div');
            container.className = 'messages-wrapper';
            container.id = 'messages-wrapper';
            document.body.appendChild(container);
        }

        container.innerHTML = '';

        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${level}`;

        // SVG-иконки в точности как в Django-шаблоне
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

        // Собираем точную структуру верстки
        alertEl.innerHTML = `
            ${iconSvg}
            <span class="alert-text">${message}</span>
            <button type="button" class="alert-close" onclick="dismissAlert(this.closest('.alert'))" title="Закрыть">&times;</button>
        `;

        container.appendChild(alertEl);

        // Автоматическое угасание через 4 секунды
        setTimeout(() => {
            dismissAlert(alertEl);
        }, 4000);
    }
});

$(document).ready(function () {
    // Получаем CSRF-токен из формы
    const getCsrfToken = () => $('[name=csrfmiddlewaretoken]').val();

    // Кастомный рендеринг пунктов выпадающего списка Select2
    function formatCategoryOption(option) {
        // Если это плейсхолдер или пустой пункт — возвращаем стандартный текст
        if (!option.id) {
            return option.text;
        }

        // Создаем DOM-структуру пункта с крестиком
        const $container = $(`
            <div class="select2-category-item">
                <span class="select2-category-title">${option.text}</span>
                <button type="button" class="select2-category-delete-btn" title="Удалить категорию">&times;</button>
            </div>
        `);

        // Обработчик клика на крестик удаления
        const $deleteBtn = $container.find('.select2-category-delete-btn');

        // 1. Блокируем события мыши, чтобы Select2 не перехватил их и не выбрал пункт
        $deleteBtn.on('mousedown mouseup', function (e) {
            e.stopPropagation();
        });

        // 2. Обрабатываем сам клик удаления
        $deleteBtn.on('click', function (e) {
            e.stopPropagation();
            e.preventDefault();

            const categoryName = option.text;
            const confirmDelete = confirm(`Вы действительно хотите удалить категорию «${categoryName}» и ВСЕ связанные с ней услуги?`);

            if (confirmDelete) {
                const deleteUrl = typeof DELETE_SERVICES_URL !== 'undefined' ? DELETE_SERVICES_URL : '/services/delete';

                // Отправляем запрос через HTMX
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

    // Инициализация Select2 с шаблоном
    $('.select2-creatable').select2({
        tags: true,
        placeholder: "Выберите или введите категорию",
        allowClear: true,
        width: '100%',
        templateResult: formatCategoryOption
    });
});