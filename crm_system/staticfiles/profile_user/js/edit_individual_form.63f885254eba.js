function deleteCurrentHint(buttonElement) {
    // Благодаря блоку див нахожу и инпут, и кнопку на удаление
    const row = buttonElement.closest('.hint-row');
    if (row) {
        row.remove();
    }
}

function addHintInput() {
    // Нахожу контейнер, где живут подсказки
    const container = document.getElementById('hints-container');

    // Создаю блок див для новых авто ответов
    const row = document.createElement('div');
    row.className = 'hint-row';
    row.style.cssText = 'display: flex; align-items: center; gap: 5px; margin-bottom: 5px;';

    // Создаю новый обьект который добавится в hints
    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.name = 'hints';
    newInput.value = '';
    newInput.placeholder = 'Введите новый автоответ...';

    // Создаю и вставляю кнопку на удаление в созданный блок див
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dash-square" style="color: rgb(248, 0, 0);" viewBox="0 0 16 16">
            <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z" />
            <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z" />
        </svg>
    `;
    // Говорю, что при нажатии на кнопку которую я добавил, вызовется другая функция на удаление 
    deleteBtn.onclick = function () { deleteCurrentHint(this); };

    // Добавляю ожидание ввода
    row.appendChild(newInput);
    // Добавляю кнопку на удаление
    row.appendChild(deleteBtn);

    // Добавляю этот новый авто-ответ в конец, где у меня вместе лежат и другие авто-ответы
    container.appendChild(row);

    newInput.focus();
}
