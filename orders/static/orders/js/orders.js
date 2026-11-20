function openOrderDrawer() {
    document.getElementById('order-drawer').classList.add('active');
    document.getElementById('drawer-overlay').classList.add('active');
    document.body.style.overflow = 'hidden'; // Блокируем прокрутку основной страницы
}

function closeOrderDrawer() {
    document.getElementById('order-drawer').classList.remove('active');
    document.getElementById('drawer-overlay').classList.remove('active');
    document.body.style.overflow = ''; // Возвращаем прокрутку

    // Отправляем глобальный сигнал: обновить все карточки заказов на странице!
    htmx.trigger(document.body, 'refreshOrders');
}

// Закрытие по нажатию клавиши ESC
// Закрытие по нажатию клавиши ESC с приоритетом верхнего сайдбара (оплаты)
document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        const paymentContainer = document.getElementById('payment-drawer-container');
        
        // Если сайдбар оплаты открыт (внутри контейнера что-то есть) — закрываем его первым
        if (paymentContainer && paymentContainer.innerHTML.trim() !== '') {
            paymentContainer.innerHTML = '';
        } else {
            // Иначе закрываем обычный сайдбар с данными клиента
            if (typeof closeOrderDrawer === 'function') {
                closeOrderDrawer();
            }
        }
    }
});

function changeOrderStatus(event, orderId, statusName, statusColor, updateUrl) {
    event.stopPropagation(); // Предотвращаем всплытие клика

    // 1. Мгновенно обновляем визуал кнопки в футере
    const btn = document.getElementById('status-btn-' + orderId);
    if (btn) {
        btn.style.background = statusColor;
        btn.innerHTML = statusName + ' <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem; margin-left: 4px;"></i>';
    }

    // 2. Закрываем поповер со списком статусов
    document.querySelectorAll('.status-popover-box').forEach(box => {
        box.style.display = 'none';
    });

    // 3. Тихо сохраняем статус на сервере в фоне
    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (!response.ok) {
            console.error('Ошибка сохранения статуса на сервере');
        }
    }).catch(error => {
        console.error('Ошибка сети:', error);
    });
}


// Показать подсказки при клике/фокусе
function showHints(input) {
    // Закрываем все другие открытые подсказки
    document.querySelectorAll('.custom-hints-dropdown').forEach(d => d.style.display = 'none');

    const dropdown = input.nextElementSibling;
    if (dropdown && dropdown.children.length > 0) {
        dropdown.style.display = 'block';
    }
}

// Функция переключения видимости поповера
function toggleStatusPopover(event, popoverId) {
    event.stopPropagation(); // Останавливаем клик, чтобы не открывалась карточка заказа

    var popover = document.getElementById(popoverId);
    var isVisible = popover.style.display === 'block';

    // Закрываем все остальные открытые поповеры на странице
    document.querySelectorAll('.status-popover-box').forEach(function (box) {
        box.style.display = 'none';
    });

    // Переключаем текущий
    if (!isVisible) {
        popover.style.display = 'block';
    } else {
        popover.style.display = 'none';
    }
}

document.body.addEventListener('showToast', function (event) {
    var detail = event.detail;
    if (!detail) return;

    var message = detail.message || 'Заказ успешно обновлен!';
    var container = document.getElementById('header-toast-container');

    if (container) {
        // Рендерим красивую зеленую плашку прямо в шапке
        container.innerHTML = `
            <div style="background: #e8fff3; color: #50cd89; padding: 5px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 6px; border: 1px solid #c9f7f5; white-space: nowrap;">
                <i class="fa-solid fa-circle-check"></i> ${message}
            </div>
        `;

        // Автоматически убираем сообщение через 3.5 секунды
        setTimeout(function () {
            container.innerHTML = '';
        }, 3500);
    }
});

// Функция для отрисовки красивого всплывающего уведомления в стиле вашей CRM
function showToastNotification(message, level) {
    // Удаляем старый тоаст, если он уже висит
    var existingToast = document.getElementById('crm-dynamic-toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Создаем элемент тоаста
    var toast = document.createElement('div');
    toast.id = 'crm-dynamic-toast';

    // Цвет в зависимости от статуса (успех — фиолетовый/зеленый, ошибка — красный)
    var bgCol = level === 'success' ? '#8950fc' : '#f64e60';

    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${bgCol};
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        font-family: inherit;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        z-index: 99999;
        display: flex;
        align-items: center;
        gap: 10px;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
    `;

    toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;
    document.body.appendChild(toast);

    // Плавное появление
    setTimeout(function () {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);

    // Автоматическое скрытие через 3.5 секунды
    setTimeout(function () {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(function () {
            toast.remove();
        }, 300);
    }, 3500);
}

document.body.addEventListener('updateNewCounter', function (event) {
    var detail = event.detail;

    // Универсальная защита: если прилетел объект, пытаемся достать значение, иначе берем как есть
    var newCount = (typeof detail === 'object' && detail !== null)
        ? (detail.count !== undefined ? detail.count : Object.values(detail)[0])
        : detail;

    // Находим элемент счетчика и обновляем текст
    var counterEl = document.querySelector('.crm-counter');
    if (counterEl) {
        counterEl.textContent = 'Новых заказов: ' + newCount;
    }
});

// Глобальный клик: закрывает поповеры, если кликнули в любое другое место экрана
document.addEventListener('click', function (e) {
    // Если кликнули НА сам поповер или внутрь него — ничего не делаем, выходим
    if (e.target.closest('.status-popover-box') || e.target.closest('button[hx-get*="change_status_order"]')) {
        return;
    }
    
    document.querySelectorAll('.status-popover-box').forEach(function (box) {
        box.style.display = 'none';
    });
});

// Фильтрация при наборе текста
function filterHints(input) {
    const filter = input.value.toLowerCase();
    const dropdown = input.nextElementSibling;
    const items = dropdown.querySelectorAll('li');

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(filter) ? 'block' : 'none';
    });

    dropdown.style.display = 'block';
}

// Выбор варианта из списка
function selectHint(li, value) {
    const input = li.closest('.custom-autocomplete-wrapper').querySelector('input');
    const currentValue = input.value.trim();

    if (currentValue) {
        // Разделяем уже введенные значения по запятой, чтобы проверить на дубликаты
        const items = currentValue.split(',').map(item => item.trim());

        // Если такого значения еще нет в инпуте, добавляем его через запятую
        if (!items.includes(value)) {
            input.value = currentValue + ', ' + value;
        }
    } else {
        // Если поле было пустым, просто записываем значение
        input.value = value;
    }

    // Скрываем список подсказок после выбора
    li.parentElement.style.display = 'none';
}

// Закрытие подсказок при клике вне поля
document.addEventListener('click', function (e) {
    if (!e.target.closest('.custom-autocomplete-wrapper')) {
        document.querySelectorAll('.custom-hints-dropdown').forEach(d => d.style.display = 'none');
    }
});

// Переключение видимости поля предоплаты
function togglePrepayInput(checkbox) {
    const container = document.getElementById('prepay-amount-container');
    const input = document.getElementById('prepay-amount-input');

    if (checkbox.checked) {
        container.style.display = 'block';
        input.focus();
    } else {
        container.style.display = 'none';
        input.value = ''; // сбрасываем значение при выключении
    }
}

// Форматирование числа с разделителями тысяч (1 000, 2 500)
function formatMoneyInput(input) {
    // Оставляем только цифры
    let value = input.value.replace(/\D/g, '');
    if (value) {
        // Превращаем в число и форматируем по русской локали (с пробелами)
        value = Number(value).toLocaleString('ru-RU');
    }
    input.value = value;
}

// Перед отправкой формы убираем пробелы из суммы, чтобы бэкенд получил чистое число
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('create-order-form');
    if (form) {
        form.addEventListener('submit', function () {
            const prepayInput = document.getElementById('prepay-amount-input');
            if (prepayInput && prepayInput.value) {
                prepayInput.value = prepayInput.value.replace(/\s/g, '');
            }
        });
    }
});

function handleClientFocus(currentInput) {
    // Определяем, какое поле сейчас в фокусе, а какое — соседнее
    const fieldName = currentInput.name;
    const oppositeFieldKey = fieldName === 'name' ? 'phone' : 'name';

    // Находим блок подсказок противоположного поля и очищаем его
    const oppositeDropdown = document.getElementById('suggestions-' + oppositeFieldKey);
    if (oppositeDropdown) {
        oppositeDropdown.innerHTML = '';
    }
}

function toggleDateRange(select) {
    const rangeWrapper = document.getElementById('custom-date-range');
    if (select.value === 'custom') {
        rangeWrapper.classList.remove('hidden');
    } else {
        rangeWrapper.classList.add('hidden');
        // Очищаем интуитивно даты при скрытии, чтобы не мешали фильтрации
        document.getElementById('date_start_input').value = '';
        document.getElementById('date_end_input').value = '';
        // Триггерим событие change на форме, чтобы HTMX отправил запрос сброса дат
        htmx.trigger('#filter-form', 'change');
    }
}

function resetDateRange() {
    const select = document.getElementById('history_date_select');
    select.value = '';
    toggleDateRange(select);
}

// Автоматически очищаем форму при обычной загрузке/перезагрузке страницы, если в URL нет параметров
document.addEventListener("DOMContentLoaded", function () {
    if (!window.location.search) {
        const form = document.getElementById('filter-form');
        if (form) {
            form.reset();
        }
    }
});

function toggleDateRange(select) {
    const rangeWrapper = document.getElementById('custom-date-range');
    if (select.value === 'custom') {
        rangeWrapper.classList.remove('hidden');
    } else {
        rangeWrapper.classList.add('hidden');
        document.querySelector('input[name="date_start_input"]').value = '';
        document.querySelector('input[name="date_end_input"]').value = '';
        htmx.trigger('#filter-form', 'change');
    }
}

function resetDateRange() {
    const select = document.getElementById('history_date_select');
    select.value = '';
    toggleDateRange(select);
}

function togglePrepayInput(checkbox) {
    const container = document.getElementById('prepay-amount-container');
    if (!container) return;

    if (checkbox.checked) {
        container.style.display = 'block';
        const input = container.querySelector('input');
        if (input) input.focus();
    } else {
        container.style.display = 'none';
        const input = container.querySelector('input');
        if (input) input.value = ''; // Очищаем сумму при выключении тумблера
    }
}

// Функция форматирования чисел при вводе (добавляет пробелы между тысячами)
function formatMoneyInput(input) {
    let value = input.value.replace(/\D/g, '');
    if (value === '') {
        input.value = '';
        return;
    }
    input.value = Number(value).toLocaleString('ru-RU');
}

// Перехват отправки HTMX для автоматической очистки пробелов перед отправкой на бэкенд
document.addEventListener('htmx:configRequest', function(evt) {
    const form = document.getElementById('payment-form');
    if (form && evt.detail.elt === form) {
        const priceInput = document.getElementById('summary-price-field');
        if (priceInput) {
            // Убираем все пробелы, чтобы на сервер улетело чистое число (например: "305000")
            evt.detail.parameters['summary_price'] = priceInput.value.replace(/\s/g, '');
        }
    }
});

function validatePrepayForm(event) {
    // Находим чекбокс (тумблер) предоплаты и инпут суммы
    const prepayCheckbox = document.querySelector('input[name="prepay"]');
    const prepayInput = document.querySelector('input[name="prepay_amount"]');

    // Если тумблер включен
    if (prepayCheckbox && prepayCheckbox.checked) {
        // Проверяем значение поля ввода (очищаем от пробелов)
        const value = prepayInput ? prepayInput.value.replace(/\s+/g, '').trim() : '';

        // Если поле пустое или равно 0
        if (!value || parseInt(value) === 0) {
            event.preventDefault(); // Останавливаем отправку формы (включая HTMX-запрос)

            // Выводим предупреждение (можно заменить на твою систему уведомлений/тостов)
            alert('Тумблер предоплаты включен, но сумма не указана. Пожалуйста, введите сумму!');

            if (prepayInput) {
                prepayInput.focus(); // Фокусируемся на поле ввода
                prepayInput.style.borderColor = '#e53e3e'; // Красная рамка для привлечения внимания

                // Убираем красную рамку при начале ввода
                prepayInput.oninput = function () {
                    this.style.borderColor = '';
                };
            }
            return false; // Отменяем отправку
        }
    }
    return true; // Разрешаем отправку
}

function selectWorker(fieldKey, workerFullName) {
    const input = document.getElementById(`id_${fieldKey}`);
    if (input) {
        input.value = workerFullName;
    }
    // Очищаем блок подсказок
    const suggestionsDiv = document.getElementById(`suggestions-${fieldKey}`);
    if (suggestionsDiv) {
        suggestionsDiv.innerHTML = '';
    }
}

function formatPhoneInput(input) {
    // Очищаем всё, кроме цифр
    let numbers = input.value.replace(/\D/g, '');

    if (numbers.length === 0) {
        input.value = '';
        return;
    }

    // Если первая цифра 8, автоматически меняем на 7 (для привычного ввода)
    if (numbers[0] === '8') {
        numbers = '7' + numbers.slice(1);
    }

    let result = '+';

    // Формируем строку по маске +X (XXX) XXX XX-XX
    if (numbers.length > 0) {
        result += numbers.substring(0, 1);
    }
    if (numbers.length > 1) {
        result += ' (' + numbers.substring(1, 4);
    }
    if (numbers.length > 4) {
        result += ') ' + numbers.substring(4, 7);
    }
    if (numbers.length > 7) {
        result += ' ' + numbers.substring(7, 9);
    }
    if (numbers.length > 9) {
        result += '-' + numbers.substring(9, 11);
    }

    input.value = result;
}

// Глобальный клик для закрытия выпадающих списков поиска клиентов/работников
document.addEventListener('click', function (event) {
    // Проверяем, был ли клик совершен вне блока формы группы (инпут + выпавший список)
    const formGroups = document.querySelectorAll('.form-group');

    formGroups.forEach(group => {
        // Если клик произошел НЕ внутри текущей группы поля
        if (!group.contains(event.target)) {
            const dropdown = group.querySelector('.client-dropdown-suggestions');
            if (dropdown) {
                dropdown.innerHTML = ''; // Очищаем содержимое (список закрывается)
            }
        }
    });
});

