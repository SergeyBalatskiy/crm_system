from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.models import FormsForOrder

@method_decorator(login_required(), name='dispatch')
class FormsForOrdersEdit(TemplateView):

    # ВАЖНО ЗАПОМНИТЬ!
    template_name = 'profile_user/form-editor.html'

    # Если я работаю с тем, чтобы в какой то области отобразить нужный для меня кусочек информации, то ОБЯЗАТЕЛЬНО
    # Необходимо делать это так, чтобы важная информация была упакована в другой HTML шаблон, который НЕ
    # будет отображаться полностью и копировать к примеру весь главный сайт с только лишь одной необходимой внут-
    # рянкой
    # То есть: при if request.headers.get('HX-Request') == 'true': (в данном случае я хочу отобразить в нужном месте нужную информацию)
    # Я НЕ ДОЛЖНЕН ссылаться на template_name ('profile_user/form-editor.html') - потому что таким образом я создаю весь сайт внутри
    # всего сайта, это билебирда
    # А вот написание form_orders_file ('profile_user/orders_file/forms_show.html') покажет то, что он рендерит 
    # именно ту область кода(сайта), которая мне и нужна!
    form_orders_file = 'profile_user/orders_file/forms_show.html'

    ALL_CRM_FIELDS = {
    'client_info': [
        {'field_key': 'name', 'label': 'Имя клиента', 'type': 'text'},
        {'field_key': 'phone', 'label': 'Телефон', 'type': 'phone'},
        {'field_key': 'telegram', 'label': 'Телеграм', 'type': 'text'},
        {'field_key': 'address', 'label': 'Адрес клиента', 'type': 'text'},
        {'field_key': 'ad_source', 'label': 'Рекламный источник', 'type': 'select'},
        {'field_key': 'email', 'label': 'Email', 'type': 'email'},
    ],
    'device_info': [
        {'field_key': 'serial_number', 'label': 'Серийный номер / IMEI', 'type': 'text'},
        {'field_key': 'type_of_device', 'label': 'Тип устройства', 'type': 'select'},
        {'field_key': 'device_company', 'label': 'Марка', 'type': 'select'},
        {'field_key': 'model', 'label': 'Модель', 'type': 'text'},
        {'field_key': 'color', 'label': 'Цвет', 'type': 'text'},
        {'field_key': 'visual', 'label': 'Внешний вид', 'type': 'select'},
        {'field_key': 'destroyed', 'label': 'Неисправность', 'type': 'text'},
        {'field_key': 'complectation', 'label': 'Комплектация', 'type': 'select'},

    ],
    'bonus_information' : [
        {'field_key': 'comment_of_order', 'label': 'Комментарий приемщика', 'type': 'textarea'},
        {'field_key': 'master', 'label': 'Мастер', 'type': 'select'},
        {'field_key': 'manager', 'label': 'Менеджер', 'type': 'select'},
        {'field_key': 'prepay', 'label': 'Предоплата', 'type': 'checkbox'},
        {'field_key': 'day_of_the_end', 'label': 'Крайний срок', 'type': 'text'},
        {'field_key': 'target_price', 'label': 'Ориентировочная цена', 'type': 'number'},
        {'field_key': 'urgently', 'label': 'Срочно', 'type': 'checkbox'},
    ]
}

    def get(self, request, *args, **kwargs):

        # Узнаю, передавалось ли подключение через HTMX или нет?
        if request.headers.get('HX-Request') == 'true':
            # Используя name="type_of_order" value="" я получаю то, какой документ нужен из формы GET запроса
            type_of_order_selected = request.GET.get('type_of_order_selected')

            # После получения запроса через HTMX, я показываю именно то, чего хочет пользователь!
            order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()
            return render(request, self.form_orders_file, {'form_order' : order_information})
        
        # Если метод получения без HTMX, то по дефолту отдаю тип заказа платный!
        # .first() обязательно! Потому что он вне зависимости от того, сколько обьектов, еще и возвращает
        # в отформатированном виде и уже готовом для корректного отображения обьект
        order_information = FormsForOrder.objects.filter(type_of_order = 'paid', user = self.request.user).first()

        return render(request, self.template_name, {'form_order' : order_information})

    def post(self, *args, **kwargs):
        ...