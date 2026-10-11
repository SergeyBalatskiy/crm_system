function openOrderDrawer() {
    document.getElementById('order-drawer').classList.add('active');
    document.getElementById('drawer-overlay').classList.add('active');
    document.body.style.overflow = 'hidden'; // Блокируем прокрутку основной страницы
}

function closeOrderDrawer() {
    document.getElementById('order-drawer').classList.remove('active');
    document.getElementById('drawer-overlay').classList.remove('active');
    document.body.style.overflow = ''; // Возвращаем прокрутку
}

// Закрытие по нажатию клавиши ESC
document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        closeOrderDrawer();
    }
});