var objects_show = window.objects_show || '';
var type_of_order_selected = window.type_of_order_selected || document.getElementById('type_of_order_selected')?.value || '';

var listToAddDeletedForms = [] // Здесь у меня есть возможность удалить кастомные формы из БД

function DeleteCustomClick(button) {
    const isConfirmed = confirm('Вы уверены, что хотите полностью удалить эту форму?');
    if (!isConfirmed) {
        return; // Пользователь нажал "Отмена"
    }

    const fieldKey = button.dataset.sectionId;

    listToAddDeletedForms.push(fieldKey);

    console.log(type_of_order_selected);
    const csrfToken = getCsrfToken();
    // Отправка AJAX-запроса только после подтверждения
    htmx.ajax('POST', window.DELETE_FORM_URL, {
        values: {
            'type_of_order_selected': type_of_order_selected,
            'objects_show': objects_show,
            'deleted_custom_forms': JSON.stringify(listToAddDeletedForms),
            'csrfmiddlewaretoken': csrfToken
        }
    });
}

// Функция очистки сайдбара от уже активных на доске полей
function filterSidebarActiveFields() {
    const activeKeysOnBoard = new Set();
    document.querySelectorAll('.fields-sortable-list .field-pill[data-key]').forEach(pill => {
        const key = pill.getAttribute('data-key');
        if (key) activeKeysOnBoard.add(key);
    });
    if (typeof addedMap !== 'undefined') {
        addedMap.forEach(keysArr => {
            keysArr.forEach(k => activeKeysOnBoard.add(k));
        });
    }
    const sidebarCards = document.querySelectorAll('#right-sidebar-content .field-checkbox-card');
    sidebarCards.forEach(card => {
        let fieldKey = card.getAttribute('data-sidebar-field-key');
        if (!fieldKey) {
            const onclickAttr = card.getAttribute('onclick') || '';
            const match = onclickAttr.match(/'([^']+)'/g);
            if (match && match[1]) {
                fieldKey = match[1].replace(/'/g, '');
            }
        }
        if (fieldKey && activeKeysOnBoard.has(fieldKey)) {
            card.remove();
        }
    });
}
document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target.id === 'right-sidebar-content') {
        filterSidebarActiveFields();
        if (typeof map !== 'undefined') {
            map.forEach((deletedKeysArray, categoryId) => {
                deletedKeysArray.forEach(fieldKey => {
                    const label = deletedLabelsMap.get(fieldKey) || fieldKey;
                    const isCustom = fieldKey.startsWith('custom-');
                    addCardToSidebar(categoryId, fieldKey, label, isCustom);
                });
            });
        }
    }
});

// Функция, отвечающая за подсчет уже добавленных форм (+ "пустышки")
function ensureTrailingPlaceholder(sectionId) {
    const container = document.getElementById(`sortable-${sectionId}`);
    if (!container) return;
    const items = container.querySelectorAll('.field-pill, .placeholder-slot');
    if (items.length % 2 !== 0) {
        const trailingSlot = document.createElement('div');
        trailingSlot.id = `slot-${sectionId}-trailing`;
        trailingSlot.className = 'placeholder-slot empty-grid-slot';
        trailingSlot.setAttribute('data-key', 'empty_for_add');
        trailingSlot.setAttribute('onclick', `openSidebarForSlot('${sectionId}', '${trailingSlot.id}')`);
        trailingSlot.innerHTML = '+ Добавить поле';
        container.appendChild(trailingSlot);
    }
}
// Выбор определенной формы и вставка/удаление из правого сайдбара
function insertFieldIntoSlot(categoryId, fieldKey, fieldLabel) {
    removeCardFromSidebar(fieldKey);

    showSaveBar();
    // Логика map с получением и просчетом длинны
    let wasRestored = false;
    if (map.has(categoryId)) {
        let existingArray = map.get(categoryId);
        const initialLength = existingArray.length;
        existingArray = existingArray.filter(keyInMap => keyInMap !== fieldKey);
        if (existingArray.length < initialLength) {
            wasRestored = true;
        }
        map.set(categoryId, existingArray);
    }
    if (!wasRestored) {
        if (!addedMap.has(categoryId)) {
            addedMap.set(categoryId, []);
        }
        const arr = addedMap.get(categoryId);
        if (globalAddPosition === 'right') {
            // Если нажали правую кнопку с +, то СНАЧАЛА добавляем "пустышку", потом уже реальный обьект (вбыранный)
            if (!arr.includes('empty_for_add')) arr.push('empty_for_add');
            if (!arr.includes(fieldKey)) arr.push(fieldKey);
        } else {
            // Обычное добавление
            if (!arr.includes(fieldKey)) arr.push(fieldKey);
        }
    }
    const container = document.getElementById(`sortable-${categoryId}`);
    if (!container) return;
    const typeOfOrder = document.getElementById('type_of_order_selected')?.value || '';
    const baseUrl = window.GET_FIELD_MODAL_URL || '/profile/get-individual-field-modal/';
    const modalUrl = `${baseUrl}?section_id=${categoryId}&field_key=${fieldKey}&type_of_order_selected=${typeOfOrder}&category=${categoryId}&field_label=${encodeURIComponent(fieldLabel)}`;
    // Отрисовка только что созданной, но еще не прошедшей сохранение формы
    const pillHTML = `
<div class="field-pill" data-key="${fieldKey}">
    <span class="drag-handle" title="Зажмите, чтобы перетащить">⋮⋮</span>
    <div class="outer-wrapper">
        <span class="field-name">${fieldLabel}</span>
        
        <!-- Обертка, которая держит кнопки вместе у правого края -->
        <div class="field-actions">
            <button type="button" class="btn" data-section-id="${categoryId}" data-field-key="${fieldKey}" onclick="DeleteClick(this)">
                <i class="fa-solid fa-trash" style="color: rgb(248, 0, 0);"></i>
            </button>
            <button type="button" class="btn" hx-get="${modalUrl}" hx-target="#center-modal-container" onclick="openFieldModal()" title="Настройки поля">
                <i class="fa fa-cogs" aria-hidden="true"></i>
            </button>
        </div>
        
    </div>
</div>
`;
    // Прячу текст "В этой секции пока нет активных полей"
    const emptyText = container.querySelector('.empty-section-placeholder');
    if (emptyText) emptyText.remove();
    if (activeSlotId) {
        const slot = document.getElementById(activeSlotId);
        if (slot) {
            slot.outerHTML = pillHTML;
        }
    } else if (globalAddPosition === 'right') {
        const placeholderId = 'slot-' + Math.random().toString(36).substr(2, 9);
        // Даю "пустышке" параметры как от реальной формы (для удобной обработки)
        const fakeEmptySlotHTML = `
            <div id="${placeholderId}" class="placeholder-slot empty-grid-slot" data-key="empty_for_add" onclick="openSidebarForSlot('${categoryId}', '${placeholderId}')">
                + Добавить поле
            </div>
        `;
        // Вставляю "пустышку"
        container.insertAdjacentHTML('beforeend', fakeEmptySlotHTML);
        // Потом реальный обьект
        container.insertAdjacentHTML('beforeend', pillHTML);
        // Добавляю в "специальный" словарь информацию, что это именно "пустышка"
        if (addedMap.has(categoryId)) {
            addedMap.get(categoryId).push('empty_for_add');
        } else {
            addedMap.set(categoryId, ['empty_for_add']);
        }
    } else {
        // Вставка формы слева 
        container.insertAdjacentHTML('beforeend', pillHTML);
    }
    if (window.htmx) {
        htmx.process(container);
    }
    closeSidebar();
    activeSlotId = null;
    globalAddPosition = null;
    if (typeof initSortables === 'function') {
        initSortables();
    }
    ensureTrailingPlaceholder(categoryId)
}