// form-removal.js

// Переинициализация DAL при замене содержимого через HTMX
document.body.addEventListener('htmx:afterSettle', function (evt) {
    if (window.jQuery) {
        window.jQuery(document).trigger('dal-init-function');
    }
});