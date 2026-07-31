from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.http import HttpResponse
from profile_user.models import FormsForOrder
import json
import ast

@method_decorator(login_required(), name='dispatch')
class FormsForOrdersEdit(TemplateView):

    # ВАЖНО ЗАПОМНИТЬ!
    template_name = 'profile_user/forms-editor.html'
    # Если я работаю с тем, чтобы в какой то области отобразить нужный для меня кусочек информации, то ОБЯЗАТЕЛЬНО
    # Необходимо делать это так, чтобы важная информация была упакована в другой HTML шаблон, который НЕ
    # будет отображаться полностью и копировать к примеру весь главный сайт с только лишь одной необходимой внут-
    # рянкой
    # То есть: при if request.headers.get('HX-Request') == 'true': (в данном случае я хочу отобразить в нужном месте нужную информацию)
    # Я НЕ ДОЛЖНЕН ссылаться на template_name ('profile_user/form-editor.html') - потому что таким образом я создаю весь сайт внутри
    # всего сайта, это билебирда
    # А вот написание form_orders_file ('profile_user/orders_file/forms_show.html') покажет то, что он рендерит 
    # именно ту область кода(сайта), которая мне и нужна!
    form_orders_file = 'profile_user/current_forms/form_show.html'
    individual_window_forms = 'profile_user/individual-window-forms/show_window_forms.html'

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

            # Сначала собираю инфу о том, откуда к нам пришел запрс (из какого места) благодаря переменным:

            # Тип заказа
            type_of_order_selected = request.GET.get('type_of_order_selected')

            # Выбранный обьект
            objects_show = request.GET.get('objects_show')

            print(type_of_order_selected, objects_show)

            # Если в результате проверки выяснится, что у нас отсутствует хоть 1 обьект, значит, мы пришли
            # сюда (request.headers.get('HX-Request') == 'true':) благодаря только лишь выбору типа заказа
            if objects_show and type_of_order_selected:
                
                # Получаю информацию о самом JSON
                order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

                #  Список, куда передаются активные формы из БД
                current_forms = []

                # Цикл который это делает
                for sec in order_information.json_forms.get('sections', []):
                    if sec['id'] == objects_show:
                        for field in sec.get('fields', []):
                            current_forms.append(field['field_key'])

                # Список, куда передаются те формы, которые НЕ задействованы в данный момент
                irrelevant_forms = []

                # Цикл который это делает
                for obj_info in self.ALL_CRM_FIELDS.get(objects_show, []):
                    if obj_info['field_key'] not in current_forms:
                        irrelevant_forms.append(obj_info)
                return render(request, self.individual_window_forms, {'irrelevant_forms' : irrelevant_forms, 'objects_show': objects_show, 'type_of_order_selected': type_of_order_selected})
            
            # После получения запроса через HTMX, я показываю именно то, чего хочет пользователь!
            order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()
            return render(request, self.form_orders_file, {'form_order' : order_information})

        message = "Вы еще не выбрали ни один тип заказов."
        return render(request, self.template_name, { 'message' : message })

    def post(self, request, *args, **kwargs):

        # Если запрос включает в себя переданный "ordered_keys" (из js с ajax запросом POST), то вызываю другую функцию:
        if 'ordered_keys' in request.POST:
            return self._save_fields_order(request)
        
        # Добавить обработку метода POST, следить за тем, пришел ли к нам запрос с заполненной переменной 'list_deleted_forms'
        # если да, то вызываю определенную функцию(_delete_selected_forms) и после, рендерю заново страницу с сообщением о успешном
        # сохранении!
        if 'list_deleted_forms' in request.POST:
            return self._delete_selected_forms(request)
        
        # Выбранная категория (само окно куда добавляются формы)
        objects_show = request.POST.get('objects_show')

        # Выбранные формы для добавления
        selected_forms = request.POST.getlist('selected_forms')

        # Выбранный тип заказа
        type_of_order_selected = request.POST.get('type_of_order_selected')

        # Если все есть:
        if objects_show and selected_forms and type_of_order_selected:
            
            # Получаю обьект из БД
            order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

            for section in order_information.json_forms.get('sections', []):
                if section['id'] == objects_show:
                    # Беру обьект всего списка из БД
                    forms_list = section.get('fields', [])
                    
                    
                    # Прохожу по каждому обьекту, который выбрал пользователь в добавление формы
                    for key in selected_forms:

                        # Добираюсь до того обьекта, который выбран (из всего полного словаря JSON)
                        for i in self.ALL_CRM_FIELDS.get(objects_show, []):

                            # Когда у нас находится совпадение между обоими словарями {} (сравнение) {}
                            if i['field_key'] == key:
                                forms_list.append({
                                    'order': len(forms_list) + 1,
                                    'label': i['label'],
                                    'field_key': i['field_key'],
                                    'type': i['type']
                                })
                                break

            # Сохраняю список (перезаписанный) от обьекта
            order_information.save()

            return render(request, self.form_orders_file, {'form_order': order_information})
        
        return render(request, self.template_name)
    
    def _save_fields_order(self, request):
            
            # Местоположение форм (секции и их айди)
            section_id = request.POST.get('section_id')

            # Тип заказа
            type_of_order = request.POST.get('type_of_order_selected')

            # Распаковываю именно весь список
            ordered_keys = request.POST.getlist('ordered_keys')

            # Достаю именно тот обьект из БД который связан с типом заказа
            order_information = FormsForOrder.objects.filter(type_of_order = type_of_order, user = self.request.user).first()

            # Беру JSON определенного типа заказа и для удобства записываю в переменную
            json_data = order_information.json_forms

            # Добираюсь до самого обьекта, где хранится тип категории ('id')
            for section_name, sections_list in json_data.items():
                for section in sections_list:
                    if str(section.get('id')) == str(section_id):

                        # Получаю весь ДЕЙСТВУЮЩИЙ список у этой категории
                        current_fields = section.get('fields', [])

                        # Запаковываю каждую форму в field_key
                        # 'master': {'field_key': 'master', 'label': 'Мастер', ...}
                        fields_by_key = {f['field_key']: f for f in current_fields if 'field_key' in f}
                        
                        # Отвечает за прохождение по каждой форме И сохранение нового порядка благодаря записи в список по очереди
                        reordered_fields = [fields_by_key[key] for key in ordered_keys if key in fields_by_key]

                        # Отдаю все то, что лежит в БД В СПИСОК
                        missing_fields = [f for f in current_fields if f.get('field_key') not in ordered_keys]

                        # Соединяю все то, что получилось из 2 списков
                        section['fields'] = reordered_fields + missing_fields

                        # Завершаем сохранение
                        break

            # Сохраняю сам новый порядок
            order_information.json_forms = json_data
            order_information.save()

            return HttpResponse(status=200)
    
    def _delete_selected_forms(self, request):

        #--------------------------------------------------------
        # JSON с заявками на удаление (в строковом формате)
        json_string_forms = request.POST.get('list_deleted_forms')
        #--------------------------------------------------------

        # Преобразую из JSON (string) в привычный обьект для работы
        # словарь с заявками на удаление 
        forms_to_delete = json.loads(json_string_forms)

        # Тип заказа
        type_of_order_selected = request.POST.get('type_of_order_selected')

        # Сделать так, чтобы в БД удалялись ненужные формы

        {'client_info': [
            "{'type': 'text', 'label': 'Имя клиента', 'order': 1, 'field_key': 'name', 'is_required': True}"
            ], 
        'device_info': [
            "{'type': 'select', 'label': 'Марка', 'order': 3, 'field_key': 'device_company', 'is_required': False}", 
            "{'type': 'select', 'label': 'Тип устройства', 'order': 2, 'field_key': 'type_of_device', 'is_required': False}"
            ], 
        'bonus_information': [
            "{'type': 'select', 'label': 'Менеджер', 'order': 3, 'field_key': 'manager', 'is_required': False}"
            ]
        }


        # Достаю именно тот обьект из БД который связан с типом заказа
        order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

        # Беру JSON определенного типа заказа и для удобства записываю в переменную
        json_models_data = order_information.json_forms

        # Для начала прохожусь по JSON (forms_to_delete) - каждой категории - 'device_info', 'bonus_information' и т.д.
        for current_category_to_delete in forms_to_delete:

            # Беру по одному обьекту (со всем содержимым)
            for objects_info_category in json_models_data.get('sections', []):

                #  Если текущая категория на удаление РАВНА категории обьекта из БД (id):
                if current_category_to_delete == objects_info_category['id']:

                    # Беру обьект (ключ и значение) из заявок на удаление
                    for key, selected_objects_to_delete in forms_to_delete.items():
                        
                        # Если КЛЮЧ == текущей выбранной категории (чтобы удалить именно те элементы в списке, которые относятся к 
                        # текущей категории)
                        if key == current_category_to_delete:

                            # Беру один обьект из списка, который ОТ заявок на удаление (обьект относится к текущей категории)
                            for one_obj in selected_objects_to_delete:
                                
                                # Из "{'type': 'select', 'label': 'Менеджер', 'order': 3, 'field_key': 'manager', 'is_required': False}"
                                # убираю кавычки:
                                # {'type': 'select', 'label': 'Менеджер', 'order': 3, 'field_key': 'manager', 'is_required': False}
                                one_obj = ast.literal_eval(one_obj)

                                # Записываю в переменную текущий список из БД (по конкретной категории) ('fields')
                                current_lst_from_model = objects_info_category.get('fields', [])

                                # Удаляю текущий обьект, выбранный из заявок на удаление
                                current_lst_from_model.remove(one_obj)

        # Сохраняю сам новый порядок (после изменения списка)
        order_information.json_forms = json_models_data
        order_information.save()

        return HttpResponse(status=204)



