// Относится к create_workers.html
// Ищет все формы, которые существуют
let WorkersdForm = document.querySelectorAll(".workers-form")

// Указывает на то, в какую область вставлять новые "блоки" с формой для сотрудников
let container = document.querySelector("#form-container")

// Тут я навешиваю кнопке функцию о добавлении новой формы
let addButton = document.querySelector("#add-form")

// Он добавляет новый счетчик, чтобы джанго понимал, какая эта форма по счету
let totalForms = document.querySelector("#id_form-TOTAL_FORMS")

// Точно указывает сколько у нас форм всего на сайте для джанго
let formNum = WorkersdForm.length

// Так сказать позволяет создаться новой форме при взаимодействии с кнопкой
addButton.addEventListener('click', addForm)

// Функция, которая будет отвечать за addForm
function addForm(e) {
    // Очень важный параметр, который говорит о том, чтобы форма с данным типом кнопки
    // не отправляла в джанго запрос о ее создании, а всего лишь работала "по одаль от нее"
    e.preventDefault()

    // Клонируем нашу оригинальную форму
    let newForm = WorkersdForm[0].cloneNode(true)

    // Ищем формы по определенным фильтрам
    let formRegex = RegExp(`form-(\\d){1}-`, 'g')

    // Отвечает за увеличение количества форм на сайте
    // не забываем про:
    // let formNum = WorkersdForm.length
    formNum++

    // Так как мы скопировали старую форму (оригинальную), то теперь нам нужно индекс этой 
    // формы поменять под ее текущее новое число
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`)

    // Вставляем нашу новую скопированную форму в ту область, где ей место!
    container.insertBefore(newForm, addButton)

    // Обновляем наш счетчик на сайте
    totalForms.setAttribute('value', `${formNum + 1}`)
}