// Взаимодействует с id самой категории
const modal = document.getElementById('categoryModal');

// Здесь вставляется текущая категория
const inputId = document.getElementById('form_id');

// Здесь вписывается тот текст, который я задаю в категории
const inputName = document.getElementById('form_name');

// Меняет цвет самого статуса категории
const inputColor = document.getElementById('form_color');

// Позволяет выбрать конкретную категорию которую мы выбрали
const selectCategory = document.getElementById('form_category');

// Он отвечает за оповещения добавления/изменения
const modalTitle = document.getElementById('modalTitle');

// Хранит ссылку на удаление категории
const deleteBtn = document.getElementById('deleteBtn');

// Функция открытия формы для ДОБАВЛЕНИЯ
function openModalForAdd() {
    modalTitle.innerText = "Создать новую категорию";
    // Так как айдишник еще не был получен, то тогда он ПУСТ
    inputId.value = "";
    // Название тоже пустое
    inputName.value = "";
    inputColor.value = "#ff0000";
    selectCategory.value = "in_process";

    // Не показываю кнопку удалить
    deleteBtn.style.display = "none";
    // Показываю окно, которое потом, имея в себе кнопку сохранить и метод POST, сохранит
    // текущую новую категорию
    modal.style.display = "block";
}

// Функция открытия формы для РЕДАКТИРОВАНИЯ
// Если нажимается кнопка вызова функции ИЗМЕНИТЬ, ТО ВЫЗЫВАЕТСЯ openModalForEdit
function openModalForEdit(element) {
    // Показываю заголовок
    modalTitle.innerText = "Изменить категорию";
    // Достаю саму ссылку на категорию
    inputId.value = element.getAttribute('data-id');
    // Достаю имя
    inputName.value = element.getAttribute('data-name');
    // Достаю цвет
    inputColor.value = element.getAttribute('data-color');
    // Достаю категорию которую выбрали
    selectCategory.value = element.getAttribute('data-category');

    // Показываю кнопку удаления
    deleteBtn.style.display = "inline-block";
    modal.style.display = "block";
}

// Функция скрытия формы
function closeModal() {
    modal.style.display = "none";
}