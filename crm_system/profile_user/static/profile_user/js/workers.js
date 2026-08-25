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