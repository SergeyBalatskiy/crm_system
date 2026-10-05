$(document).ready(function () {
    $('.select2-creatable').select2({
        tags: true, // Включает возможность вбивать свои варианты
        placeholder: "Выберите или введите категорию",
        allowClear: true
    });
});