document.addEventListener('DOMContentLoaded', function () {
    const addFormBtn = document.getElementById('add-new-form-acceptable');
    const formsList = document.getElementById('acceptable-div-form');

    // Элемент управления количеством форм (имя зависит от префикса formset)
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    const emptyFormTemplate = document.getElementById('empty-form-acceptable').innerHTML;

    addFormBtn.addEventListener('click', function () {
        // 1. Получаем текущее количество форм
        let currentFormCount = parseInt(totalFormsInput.value);

        // 2. Заменяем __prefix__ в шаблоне на текущий индекс
        const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, currentFormCount);

        // 3. Вставляем новую форму в конец списка
        formsList.insertAdjacentHTML('beforeend', newFormHtml);

        // 4. Увеличиваем счетчик TOTAL_FORMS на 1
        totalFormsInput.value = currentFormCount + 1;
    });
});

