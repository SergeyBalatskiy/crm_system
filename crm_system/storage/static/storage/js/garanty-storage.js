// garanty-storage.js
document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'add-new-form-garanty') {
        const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
        const emptyFormContainer = document.getElementById('empty-form-garanty');
        const formsList = document.getElementById('garanty-div-form');

        if (totalFormsInput && emptyFormContainer && formsList) {
            let currentFormCount = parseInt(totalFormsInput.value);
            let newFormHtml = emptyFormContainer.innerHTML.replace(/__prefix__/g, currentFormCount);

            // Очищаем HTML от авто-сгенерированных следов Select2
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newFormHtml;
            tempDiv.querySelectorAll('.select2-container').forEach(el => el.remove());
            tempDiv.querySelectorAll('select').forEach(select => {
                select.removeAttribute('data-select2-id');
                select.classList.remove('select2-hidden-accessible');
                select.style.display = '';
            });

            formsList.insertAdjacentHTML('beforeend', tempDiv.innerHTML);
            totalFormsInput.value = currentFormCount + 1;

            // Запускаем DAL для нового поля
            if (window.jQuery) {
                window.jQuery(document).trigger('dal-init-function');
            }
        }
    }
});

$(document).on('select2:select', 'select[data-autocomplete-light-function]', function (e) {
    const data = e.params.data; // Данные, которые приходят из views.py (get_results) 
    const $formRow = $(this).closest('.django-form') // Назходит контейнер текущей формы

    // Автозаполнение в зависимости от указанных полей
    if (data.code !== undefined) {
        $formRow.find('input[name$="-individual_code_history"]').val(data.code);
    }
    if (data.code !== undefined) {
        $formRow.find('input[name$="-supplier_history"]').val(data.supplier);
    }
    if (data.code !== undefined) {
        $formRow.find('input[name$="-buy_price_history"]').val(data.price);
    }
});