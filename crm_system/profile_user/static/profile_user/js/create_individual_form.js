document.getElementById('checkbox1').addEventListener('click', function (event) {
    document.getElementById('checkbox2').checked = false;
    document.getElementById('checkbox3').checked = false;
    event.target.checked = true;
});

document.getElementById('checkbox2').addEventListener('click', function (event) {
    document.getElementById('checkbox1').checked = false;
    document.getElementById('checkbox3').checked = false;
    event.target.checked = true;
});

document.getElementById('checkbox3').addEventListener('click', function (event) {
    document.getElementById('checkbox1').checked = false;
    document.getElementById('checkbox2').checked = false;
    event.target.checked = true;
});

document.body.addEventListener('closeModal', function () {
    // Очистка контейнера
    document.getElementById('show_new_form_create').innerHTML = '';
});
