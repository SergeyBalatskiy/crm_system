document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', async (event) => {
        // Проверяем клик по кнопке удаления
        if (!event.target.classList.contains('btn-delete-worker')) return;

        const deleteButton = event.target;
        const workerCard = deleteButton.closest('.worker-place');
        if (!workerCard) return;

        const name = workerCard.dataset.name;
        const surname = workerCard.dataset.surname;

        // Получаем CSRF-токен из формы
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!confirm(`Удалить сотрудника ${name} ${surname}?`)) return;

        const formData = new FormData();
        formData.append('delete_name', name);
        formData.append('delete_surname', surname);
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                workerCard.remove();
            } else {
                alert('Не удалось удалить сотрудника.');
            }
        } catch (error) {
            console.error('Ошибка при отправке запроса:', error);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // Находим поля ввода телефона по имени или ID
    const phoneInputs = document.querySelectorAll('input[name*="phone"], input[id*="phone"]');

    phoneInputs.forEach(input => {
        input.addEventListener('input', onPhoneInput);
        input.addEventListener('keydown', onPhoneKeyDown);
    });

    function getDigits(value) {
        return value.replace(/\D/g, '');
    }

    function onPhoneInput(e) {
        let input = e.target;
        let inputNumbersValue = getDigits(input.value);
        let formattedInputValue = '';
        let selectionStart = input.selectionStart;

        if (!inputNumbersValue) {
            return input.value = '';
        }

        // Если ввод начинается с 7 или 8 — нормализуем под +7
        if (['7', '8', '9'].includes(inputNumbersValue[0])) {
            if (inputNumbersValue[0] === '9') inputNumbersValue = '7' + inputNumbersValue;
            let firstSymbols = '+7';
            formattedInputValue = firstSymbols + ' ';

            if (inputNumbersValue.length > 1) {
                formattedInputValue += inputNumbersValue.substring(1, 4);
            }
            if (inputNumbersValue.length >= 5) {
                formattedInputValue += ' ' + inputNumbersValue.substring(4, 7);
            }
            if (inputNumbersValue.length >= 8) {
                formattedInputValue += ' ' + inputNumbersValue.substring(7, 9);
            }
            if (inputNumbersValue.length >= 10) {
                formattedInputValue += ' ' + inputNumbersValue.substring(9, 11);
            }
        } else {
            // Для номеров других стран
            formattedInputValue = '+' + inputNumbersValue.substring(0, 16);
        }

        input.value = formattedInputValue;
    }

    function onPhoneKeyDown(e) {
        // Разрешаем стирание символов Backspace
        let inputValue = e.target.value.replace(/\D/g, '');
        if (e.keyCode === 8 && inputValue.length === 1) {
            e.target.value = '';
        }
    }
});