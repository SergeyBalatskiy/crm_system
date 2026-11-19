// Относится к forms-editor.html

// 1. Создаем глобальный словарь для запоминания названий удаленных полей
const deletedLabelsMap = new Map();

function cancelChanges() {
    map.clear();
    addedMap.clear();
    closeSidebar();
    hideSaveBar();
    const selectElem = document.querySelector('select[name="type_of_order_selected"]');
    const hiddenInput = document.getElementById('type_of_order_selected');
    const selectedType = (selectElem && selectElem.value)
        ? selectElem.value
        : (hiddenInput ? hiddenInput.value : '');
    if (selectedType) {
        htmx.ajax('GET', window.FORM_EDITOR_URL, {
            target: '#show-data-forms',
            swap: 'innerHTML',
            values: { 'type_of_order_selected': selectedType }
        });
    }
}

function hideSaveBar() {
    document.getElementById('bottom-save-bar').classList.add('hidden');
}

// Хранилище УДАЛЕННЫХ полей: { categoryId: ['manager', 'color'] }
const map = new Map();
const addedMap = new Map();
function extractFieldKey(rawObj) {
    if (typeof rawObj === 'string') {
        const match = rawObj.match(/['"]field_key['"]\s*:\s*['"]([^'"]+)['"]/);
        if (match) {
            return match[1]; // Вернет чистое слово, например "manager"
        }
        return rawObj;
    } else if (typeof rawObj === 'object' && rawObj !== null) {
        return rawObj.field_key || rawObj;
    }
    return rawObj;
}

// Функция кнопки удаления (красная корзина)
// Удаление (после saveChanges() итоговая отправка действующих форм)
function DeleteClick(element) {
    const dataObj = typeof element.dataset.fieldKey !== 'undefined'
        ? { id: element.dataset.sectionId, key: element.dataset.fieldKey }
        : JSON.parse(element.getAttribute('data'));
    const categoryId = String(dataObj.id);
    const fieldKey = dataObj.key || extractFieldKey(dataObj.obj);
    const pill = element.closest('.field-pill');
    const fieldNameElem = pill ? pill.querySelector('.field-name') : null;
    const fieldLabel = fieldNameElem ? fieldNameElem.innerText.trim() : fieldKey;
    deletedLabelsMap.set(fieldKey, fieldLabel);

    let wasJustAdded = false;
    showSaveBar();

    if (addedMap.has(categoryId)) {
        let addedArr = addedMap.get(categoryId);
        const initialLength = addedArr.length;

        addedArr = addedArr.filter(key => key !== fieldKey);
        addedMap.set(categoryId, addedArr);

        if (addedArr.length < initialLength) {
            wasJustAdded = true;
        }
    }

    if (!wasJustAdded) {
        if (map.has(categoryId)) {
            const existingArray = map.get(categoryId);
            if (!existingArray.includes(fieldKey)) {
                existingArray.push(fieldKey);
            }
        } else {
            map.set(categoryId, [fieldKey]);
        }
    }

    // ЕСЛИ САЙДБАР ОТКРЫТ — отправляем удаленную форму туда сразу
    if (isSidebarOpen()) {
        const isCustom = fieldKey.startsWith('custom-');
        addCardToSidebar(categoryId, fieldKey, fieldLabel, isCustom);
    }

    // Замена удаленного поля на пунктирную заглушку "+ Добавить поле"
    const placeholderId = 'slot-' + Math.random().toString(36).substr(2, 9);
    const placeholderHTML = `
    <div id="${placeholderId}" class="placeholder-slot" onclick="openSidebarForSlot('${categoryId}', '${placeholderId}')">
        + Добавить поле
    </div>
    `;

    if (pill) {
        pill.outerHTML = placeholderHTML;
    }
}

function resetFormEditorState() {
    // 1. Очищаем карты с временными данными
    if (typeof map !== 'undefined' && map.clear) map.clear();
    if (typeof addedMap !== 'undefined' && addedMap.clear) addedMap.clear();
    if (typeof deletedLabelsMap !== 'undefined' && deletedLabelsMap.clear) deletedLabelsMap.clear();

    // 2. Сбрасываем активные позиции и слоты
    activeSlotId = null;
    globalAddPosition = null;

    // 3. Закрываем правый сайдбар
    closeSidebar();

    // 4. Скрываем нижнюю панель сохранения
    hideSaveBar();
}

// Функция, проверяющая, открыт ли сейчас сайдбар с ирелевантными формами?
function isSidebarOpen() {
    const sidebar = document.getElementById('right-sidebar');
    return sidebar && !sidebar.classList.contains('hidden');
}

// Динамическое добавление карточки в открытый сайдбар
function addCardToSidebar(categoryId, fieldKey, fieldLabel, isCustom = true) {
    const container = document.getElementById('right-sidebar-content');
    if (!container) return;

    let sidebarBody = container.querySelector('.sidebar-body');
    if (!sidebarBody) {
        sidebarBody = container;
    }
    const placeholder = container.querySelector('p.placeholder-text');
    if (placeholder && placeholder.innerText.includes('добавлены')) {
        placeholder.remove();
    }

    // Проверка на дубликаты
    const existing = sidebarBody.querySelector(`[data-sidebar-field-key="${fieldKey}"]`);
    if (existing) return;

    const card = document.createElement('div');
    card.className = 'field-checkbox-card';
    card.setAttribute('data-sidebar-field-key', fieldKey);
    card.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; margin-bottom: 8px; border: 1px solid #ccc; border-radius: 6px; cursor: pointer;';

    const safeLabel = fieldLabel.replace(/'/g, "\\'");
    card.setAttribute('onclick', `insertFieldIntoSlot('${categoryId}', '${fieldKey}', '${safeLabel}')`);

    // Вызов функции DeleteCustomClick
    const trashButtonHTML = isCustom ? `
    <button type="button" 
        class="btn btn-delete-custom-field" 
        data-section-id="${fieldKey}"
        data-field-key="${fieldKey}"
        onclick="event.stopPropagation(); DeleteCustomClick(this);" 
        title="Удалить форму навсегда"
        style="background-color: #f1f3f5; border: none; padding: 6px 10px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center;">
        <i class="fa-solid fa-trash" style="color: rgb(248, 0, 0);"></i>
    </button>
` : '';

    card.innerHTML = `
        <span class="field-label">${fieldLabel}</span>
        ${trashButtonHTML}
    `;

    sidebarBody.appendChild(card);
}

// Удаление карточки из сайдбара при её выборе
function removeCardFromSidebar(fieldKey) {
    const container = document.getElementById('right-sidebar-content');
    if (!container) return;

    // Ищем карточку по data-атрибуту или onclick
    const cards = container.querySelectorAll('.field-checkbox-card');
    cards.forEach(card => {
        if (card.getAttribute('data-sidebar-field-key') === fieldKey || card.getAttribute('onclick')?.includes(`'${fieldKey}'`)) {
            card.remove();
        }
    });

    // Если в сайдбаре больше не осталось полей — выводим сообщение
    const remainingCards = container.querySelectorAll('.field-checkbox-card');
    if (remainingCards.length === 0) {
        container.innerHTML = '<p class="placeholder-text">Все доступные поля уже добавлены в эту секцию.</p>';
    }
}

// Клик по пунктирному полю для выбора новой формы (Взаимодействие с определенным полем благодаря id`шнику в "Добавить поле +" )
function openSidebarForSlot(categoryId, placeholderId) {
    activeSlotId = placeholderId;
    globalAddPosition = null;
    const currentTypeOfOrder = document.getElementById('type_of_order_selected').value;
    const deletedFormsForCategory = map.has(categoryId) ? map.get(categoryId) : [];
    const activeFields = getActiveFieldsForCategory(categoryId);
    const sidebar = document.getElementById('right-sidebar');
    sidebar.classList.remove('hidden');
    document.getElementById('right-sidebar-content').innerHTML = '<p class="placeholder-text">Загрузка...</p>';

    htmx.ajax('GET', window.FORM_EDITOR_URL, {
        target: '#right-sidebar-content',
        swap: 'innerHTML',
        values: {
            'type_of_order_selected': currentTypeOfOrder,
            'objects_show': categoryId,
            'deleted_forms_from_js': JSON.stringify(deletedFormsForCategory),
            'active_fields': JSON.stringify(activeFields)
        }
    });
}

// 1. Удаление формы из сайдбара
function deleteCustomFieldFromSidebar(fieldKey, buttonElem) {
    if (!confirm('Вы уверены, что хотите полностью удалить эту форму?')) {
        return;
    }

    // Удаляем карточку из сайдбара
    const card = buttonElem.closest('.field-checkbox-card');
    if (card) {
        card.remove();
    }

    const csrfToken = getCsrfToken();

    htmx.ajax('POST', window.FORM_EDITOR_URL || '/profile/form-editor', {
        swap: 'none',
        headers: {
            'X-CSRFToken': csrfToken
        },
        values: {
            'action': 'delete_custom_field',
            'field_key': fieldKey,
            'csrfmiddlewaretoken': csrfToken
        }
    });
}

// 2. Инициализация сортировки
function initSortable(container) {
    new Sortable(container, {
        animation: 0,
        handle: '.drag-handle',
        ghostClass: 'sortable-ghost',
        filter: '.empty-grid-slot',
        preventOnFilter: false,
        swap: true,
        swapClass: 'sortable-swap-highlight',

        onEnd: function (evt) {
            const sectionCard = evt.to.closest('.section-card');
            const sectionId = sectionCard ? sectionCard.id : '';

            const orderedKeys = Array.from(evt.to.querySelectorAll('.field-pill, .placeholder-slot'))
                .map(item => item.getAttribute('data-key'))
                .filter(key => key !== null);

            const csrfToken = getCsrfToken();
            const typeOfOrder = document.querySelector('select[name="type_of_order_selected"]')?.value
                || document.getElementById('type_of_order_selected')?.value
                || '';

            htmx.ajax('POST', window.FORM_EDITOR_URL || '/profile/form-editor', {
                swap: 'none',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                values: {
                    'ordered_keys': JSON.stringify(orderedKeys),
                    'section_id': sectionId,
                    'type_of_order_selected': typeOfOrder,
                    'csrfmiddlewaretoken': csrfToken
                }
            });
        }
    });
}

// Этот ВАЖНЫЙ кусок кода отвечает за грамотное взаимодействие между Динамическим отображением форм(в реальном времени, благодаря HTMX) и SortableJS
htmx.onLoad(function (target) {
    if (target.classList && target.classList.contains('fields-sortable-list')) {
        initSortable(target);
    } else {
        target.querySelectorAll('.fields-sortable-list').forEach(initSortable);
    }
});

// Функция для динамического считывания токена из браузера
function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) return match[1];

    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
        || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Кнопка сохранения изменений на сервер
function saveChanges() {
    const csrfToken = getCsrfToken(); // Достаем реальный хэш токена

    const mapAsObject = Object.fromEntries(map);
    const addedMapAsObject = Object.fromEntries(addedMap);
    const selectElem = document.querySelector('select[name="type_of_order_selected"]');
    const hiddenInput = document.getElementById('type_of_order_selected');
    const currentTypeOfOrder = (selectElem && selectElem.value)
        ? selectElem.value
        : (hiddenInput ? hiddenInput.value : '');
    let fieldsOrder = {};
    document.querySelectorAll('.fields-sortable-list').forEach(container => {
        let sectionId = container.getAttribute('data-section-id');
        let keys = [];
        container.querySelectorAll('.field-pill[data-key], .placeholder-slot[data-key]').forEach(item => {
            let key = item.getAttribute('data-key');
            if (key) {
                keys.push(key);
            }
        });

        fieldsOrder[sectionId] = keys;
    });

    // Отправка сохранений на сервер
    htmx.ajax('POST', window.FORM_EDITOR_URL || '/profile/form-editor', {
        swap: 'none',
        headers: {
            'X-CSRFToken': csrfToken // Передаем CSRF в заголовке
        },
        values: {
            'type_of_order_selected': currentTypeOfOrder,
            'list_deleted_forms': JSON.stringify(mapAsObject),
            'list_added_forms': JSON.stringify(addedMapAsObject),
            'fields_order': JSON.stringify(fieldsOrder),
            'csrfmiddlewaretoken': csrfToken // Заменили '{{ csrf_token }}' на переменную
        }
    }).then(() => {
        map.clear();
        addedMap.clear();
        hideSaveBar();
        closeSidebar();
        if (currentTypeOfOrder) {
            htmx.ajax('GET', window.FORM_EDITOR_URL || '/profile/form-editor', {
                target: '#show-data-forms',
                swap: 'innerHTML',
                values: { 'type_of_order_selected': currentTypeOfOrder }
            });
        }
    });
}

// Сортировщик, который распределяет правильно формы
function initSortables() {
}
document.addEventListener('DOMContentLoaded', initSortables);
document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target.id === 'show-data-forms') {
        initSortables();
    }
});


document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        // 1. Очищаем окно создания новой формы
        const createModal = document.getElementById('show_new_form_create');
        if (createModal && createModal.innerHTML.trim() !== '') {
            createModal.innerHTML = '';
        }

        // 2. Закрываем окно настроек полей (если оно открыто)
        if (typeof closeFieldModal === 'function') {
            closeFieldModal();
        }
    }
});