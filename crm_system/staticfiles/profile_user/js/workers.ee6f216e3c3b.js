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

document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.add('fade-out');
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 3500);
    });
});