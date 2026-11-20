var activeSlotId = null;       // Если кликнули по пунктиру
var globalAddPosition = null;  // 'left' или 'right', если кликнули по нижним плюсам

// Показывает удаленные категории (для того чтобы при нажатии на "Добавить слева/справа
// у меня показывались не только те формы, которые не существуют в БД, но еще и те, которые
// удалены, но не отправлены на сохранение")
function getDeletedFieldsForCategory(categoryId) {
    const id = String(categoryId);
    return map.has(id) ? map.get(id) : [];
}

// Функция сбора ключей полей, которые СЕЙЧАС находятся в DOM для данной категории
function getActiveFieldsForCategory(categoryId) {
    const keys = [];
    const container = document.querySelector(`.fields-sortable-list[data-section-id="${categoryId}"]`);

    if (container) {
        container.querySelectorAll('.field-pill[data-key], .placeholder-slot[data-key]').forEach(item => {
            const key = item.getAttribute('data-key');
            if (key && key !== 'empty_place_for_add' && key !== 'empty_for_add') {
                keys.push(key);
            }
        });
    }
    return keys; // вернет массив, например: ["phone", "email"]
}

function openSidebarGlobal(categoryId, position) {
    activeSlotId = null;
    globalAddPosition = position;

    const sidebar = document.getElementById('right-sidebar');
    sidebar.classList.remove('hidden');
}

function openFieldModal() {
    const modal = document.getElementById('field-settings-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeFieldModal() {
    const modal = document.getElementById('field-settings-modal');
    if (modal) modal.classList.add('hidden');
}

function openSidebar() {
    const sidebar = document.getElementById('right-sidebar');
    sidebar.classList.remove('hidden');
}

function closeSidebar() {
    const sidebar = document.getElementById('right-sidebar');
    sidebar.classList.add('hidden');
}

function showSaveBar() {
    const saveBar = document.getElementById('bottom-save-bar');
    saveBar.classList.remove('hidden');
}

document.querySelectorAll('.fields-sortable-list').forEach(function (element) {
    new Sortable(element, {
        animation: 0,
        handle: '.drag-handle',
        ghostClass: 'sortable-ghost',
        filter: '.empty-grid-slot',
        preventOnFilter: false,
        swap: true,
        swapClass: 'sortable-swap-highlight',

        onEnd: function (evt) {
            const sectionCard = evt.to.closest('.section-card');

            // Получаю ID секции
            const sectionId = sectionCard.dataset.sectionId || sectionCard.id;

            // Считываем ВСЕ дочерние блоки контейнера по порядку
            const orderedKeys = Array.from(evt.to.children)
                .map(item => {
                    if (item.classList.contains('field-pill')) {
                        return item.getAttribute('data-key');
                    } else if (item.classList.contains('empty-grid-slot') || item.classList.contains('add-field-slot')) {
                        return 'empty_for_add';
                    }
                    return null;
                })
                .filter(key => key !== null);

            const fieldsOrder = {
                [sectionId]: orderedKeys
            };

            const csrfToken = getCsrfToken();
            const typeOfOrder = document.querySelector('select[name="type_of_order_selected"]')?.value
                || document.getElementById('type_of_order_selected')?.value
                || '';

            // Отправка ajax POST метода
            htmx.ajax('POST', window.FORM_EDITOR_URL || '/profile/form-editor', {
                swap: 'none',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                values: {
                    'fields_order': JSON.stringify(fieldsOrder),
                    'type_of_order_selected': typeOfOrder,
                    'csrfmiddlewaretoken': csrfToken
                }
            });
        }
    });
});