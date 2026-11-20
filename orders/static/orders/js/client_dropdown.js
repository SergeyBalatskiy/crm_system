function fillClientData(name, phone) {
    // Находим инпуты в форме по их name
    const nameInput = document.querySelector('input[name="name"]');
    const phoneInput = document.querySelector('input[name="phone"]');

    // Подставляем значения
    if (nameInput) {
        nameInput.value = name;
    }
    if (phoneInput) {
        phoneInput.value = phone;
    }

    // Очищаем блоки с подсказками, чтобы они исчезли после выбора
    document.querySelectorAll('.client-dropdown-suggestions').forEach(container => {
        container.innerHTML = '';
    });
}