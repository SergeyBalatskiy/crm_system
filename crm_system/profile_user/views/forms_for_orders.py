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
        {'field_key': 'name', 'label': 'Имя клиента', 'type': 'select'},
        {'field_key': 'phone', 'label': 'Телефон', 'type': 'select'},
        {'field_key': 'telegram', 'label': 'Телеграм', 'type': 'select'},
        {'field_key': 'address', 'label': 'Адрес клиента', 'type': 'select'},
        {'field_key': 'ad_source', 'label': 'Рекламный источник', 'type': 'select'},
        {'field_key': 'email', 'label': 'Email', 'type': 'select'},
    ],
    'device_info': [
        {'field_key': 'serial_number', 'label': 'Серийный номер / IMEI', 'type': 'select'},
        {'field_key': 'type_of_device', 'label': 'Тип устройства', 'type': 'select'},
        {'field_key': 'device_company', 'label': 'Марка', 'type': 'select'},
        {'field_key': 'model', 'label': 'Модель', 'type': 'select'},
        {'field_key': 'color', 'label': 'Цвет', 'type': 'select'},
        {'field_key': 'visual', 'label': 'Внешний вид', 'type': 'select'},
        {'field_key': 'destroyed', 'label': 'Неисправность', 'type': 'select'},
        {'field_key': 'complectation', 'label': 'Комплектация', 'type': 'select'},

    ],
    'bonus_information' : [
        {'field_key': 'comment_of_order', 'label': 'Комментарий приемщика', 'type': 'textarea'},
        {'field_key': 'master', 'label': 'Мастер', 'type': 'select'},
        {'field_key': 'manager', 'label': 'Менеджер', 'type': 'select'},
        {'field_key': 'prepay', 'label': 'Предоплата', 'type': 'checkbox'},
        {'field_key': 'day_of_the_end', 'label': 'Крайний срок', 'type': 'select'},
        {'field_key': 'target_price', 'label': 'Ориентировочная цена', 'type': 'select'},
        {'field_key': 'urgently', 'label': 'Срочно', 'type': 'checkbox'},
    ]
}

    def get(self, request, *args, **kwargs):

        if request.headers.get('HX-Request') == 'true':

            type_of_order_selected = request.GET.get('type_of_order_selected')
            objects_show = request.GET.get('objects_show')

            if objects_show and type_of_order_selected:

                deleted_forms_str = request.GET.get('deleted_forms_from_js', '[]')
                try:
                    deleted_forms_from_js = json.loads(deleted_forms_str)
                except json.JSONDecodeError:
                    deleted_forms_from_js = []
                
                deleted_keys = []

                for item in deleted_forms_from_js:
                    if isinstance(item, str):
                        try:
                            parsed = ast.literal_eval(item)
                            if isinstance(parsed, dict) and 'field_key' in parsed:
                                deleted_keys.append(parsed['field_key'])
                            else:
                                deleted_keys.append(item)
                        except Exception:
                            deleted_keys.append(item)
                    elif isinstance(item, dict):
                        deleted_keys.append(item.get('field_key'))

                # 1. Запрос в БД
                order_information = FormsForOrder.objects.filter(
                    type_of_order=type_of_order_selected, 
                    user=self.request.user
                ).first()

                current_forms = []

                # 2. Безопасное извлечение текущих активных форм из БД
                if order_information and order_information.json_forms:
                    for sec in order_information.json_forms.get('sections', []):
                        # Безопасное получение id секции
                        if isinstance(sec, dict) and sec.get('id') == objects_show:
                            for field in sec.get('fields', []):
                                # Защита от None и битых словарей
                                if isinstance(field, dict) and 'field_key' in field:
                                    current_forms.append(field['field_key'])

                irrelevant_forms = []

                # 3. Фильтрация базовых форм CRM
                for obj_info in self.ALL_CRM_FIELDS.get(objects_show, []):
                    if isinstance(obj_info, dict) and 'field_key' in obj_info:
                        if obj_info['field_key'] not in current_forms or obj_info['field_key'] in deleted_keys:
                            irrelevant_forms.append(obj_info)

                # 4. Безопасная обработка кастомных полей из библиотеки
                if order_information and order_information.json_forms:
                    for section in order_information.json_forms.get('sections', []):
                        if isinstance(section, dict) and section.get('id') == objects_show:
                            custom_pool = section.get('custom_forms', [])
                            for custom_field in custom_pool:
                                if isinstance(custom_field, dict) and 'field_key' in custom_field:
                                    if custom_field['field_key'] not in current_forms:
                                        irrelevant_forms.append(custom_field)
                
                return render(
                    request, 
                    self.individual_window_forms, 
                    {
                        'irrelevant_forms': irrelevant_forms, 
                        'objects_show': objects_show, 
                        'type_of_order_selected': type_of_order_selected
                    }
                )
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
                    custom_pool = section.get('custom_forms', [])
                    
                    # Прохожу по каждому обьекту, который выбрал пользователь в добавление формы
                    for key in selected_forms:

                        # Поиск сначала в стандартных ALL_CRM_FIELDS
                        standard_field = next((item for item in self.ALL_CRM_FIELDS.get(objects_show, []) if item.get('field_key') == key), None)

                        # Поиск в обычных полях
                        if standard_field:
                            if not any(f.get('field_key') == key for f in forms_list):
                                forms_list.append({
                                    'order': len(forms_list) + 1,
                                    'label': standard_field['label'],
                                    'field_key': standard_field['field_key'],
                                    'type': standard_field['type']
                                })
                        # Поиск в кастомных полях
                        else:
                            custom_field = next((item for item in custom_pool if item.get('field_key') == key), None)
                            
                            if custom_field:
                                if not any(f.get('field_key') == key for f in forms_list):
                                    # Добавляем на форму
                                    forms_list.append({
                                        'order': len(forms_list) + 1,
                                        'label': custom_field['label'],
                                        'field_key': custom_field['field_key'],
                                        'type': custom_field['type'],
                                        'hints': custom_field.get('hints', []),
                                        'custom_form': True
                                    })
                                    # УДАЛЯЕМ из пула доступных в сайдбаре, раз оно теперь на экране!
                                    section['custom_forms'] = [f for f in custom_pool if f.get('field_key') != key]

            # Сохраняю список (перезаписанный) от обьекта
            order_information.save()

            return render(request, self.form_orders_file, {'form_order': order_information})
        
        return render(request, self.template_name)
    
    def _save_fields_order(self, request):
        section_id = request.POST.get('section_id')
        type_of_order = request.POST.get('type_of_order_selected')
        
        # Получаем сырые данные из POST
        raw_keys = request.POST.getlist('ordered_keys') or request.POST.get('ordered_keys')
        
        # Разбираем JSON-строку
        ordered_keys = []
        if isinstance(raw_keys, list) and len(raw_keys) > 0 and raw_keys[0].startswith('['):
            try:
                ordered_keys = json.loads(raw_keys[0])
            except json.JSONDecodeError:
                ordered_keys = raw_keys
        elif isinstance(raw_keys, str) and raw_keys.startswith('['):
            try:
                ordered_keys = json.loads(raw_keys)
            except json.JSONDecodeError:
                ordered_keys = [raw_keys]
        else:
            ordered_keys = raw_keys

        order_information = FormsForOrder.objects.filter(
            type_of_order=type_of_order, 
            user=self.request.user
        ).first()

        if not order_information or not order_information.json_forms:
            return HttpResponse(status=400)

        json_data = order_information.json_forms
        sections = json_data.get('sections', []) if isinstance(json_data, dict) else []

        for section in sections:
            if str(section.get('id')) == str(section_id):
                current_fields = section.get('fields', [])
                
                fields_by_key = {
                    f['field_key']: f 
                    for f in current_fields 
                    if isinstance(f, dict) and 'field_key' in f
                }

                reordered_fields = []
                for idx, key in enumerate(ordered_keys, start=1):
                    if key in fields_by_key:
                        field_obj = fields_by_key[key]
                        field_obj['order'] = idx
                        reordered_fields.append(field_obj)

                missing_fields = [
                    f for f in current_fields 
                    if isinstance(f, dict) and f.get('field_key') not in ordered_keys
                ]
                start_order = len(reordered_fields) + 1
                for idx, f in enumerate(missing_fields, start=start_order):
                    f['order'] = idx

                section['fields'] = reordered_fields + missing_fields
                break

        # Принудительно перезаписываем и сохраняем JSONField
        order_information.json_forms = dict(json_data)
        order_information.save(update_fields=['json_forms'])

        return HttpResponse(status=200)
    
    def _delete_selected_forms(self, request):

        json_string_forms = request.POST.get('list_deleted_forms', '{}')
        json_added_forms = request.POST.get('list_added_forms', '{}')

        try:
            forms_to_add = json.loads(json_added_forms)
        except json.JSONDecodeError:
            forms_to_add = {}

        try:
            forms_to_delete = json.loads(json_string_forms)
        except json.JSONDecodeError:
            forms_to_delete = {}

        type_of_order_selected = request.POST.get('type_of_order_selected')

        order_information = FormsForOrder.objects.filter(
            type_of_order=type_of_order_selected, 
            user=self.request.user
        ).first()

        if not order_information or not order_information.json_forms:
            return HttpResponse(status=204)

        json_models_data = order_information.json_forms

        for section in json_models_data.get('sections', []):
            if not isinstance(section, dict):
                continue

            category_id = section.get('id')

            # --- УДАЛЕНИЕ ЭЛЕМЕНТОВ ---
            if category_id in forms_to_delete:
                keys_to_delete = forms_to_delete[category_id]
                current_fields = section.get('fields', []) or []
                new_fields_list = []

                for field in current_fields:
                    if isinstance(field, dict):
                        if field.get('field_key') in keys_to_delete:
                            if field.get('custom_form'):
                                if 'custom_forms' not in section or not isinstance(section['custom_forms'], list):
                                    section['custom_forms'] = []
                                
                                if not any(isinstance(f, dict) and f.get('field_key') == field.get('field_key') for f in section['custom_forms']):
                                    section['custom_forms'].append(field)
                        else:
                            new_fields_list.append(field)

                section['fields'] = new_fields_list

            # --- ДОБАВЛЕНИЕ ЭЛЕМЕНТОВ ---
            if category_id in forms_to_add:
                keys_to_add = forms_to_add[category_id]
                all_category_fields = self.ALL_CRM_FIELDS.get(category_id, [])

                # Безопасно собираем существующие ключи, игнорируя None
                current_fields = section.get('fields', []) or []
                existing_keys = [f.get('field_key') for f in current_fields if isinstance(f, dict) and 'field_key' in f]

                if 'fields' not in section or not isinstance(section['fields'], list):
                    section['fields'] = []

                for key in keys_to_add:
                    if key not in existing_keys:
                        # 1. Ищем в ALL_CRM_FIELDS
                        field_obj = next((item for item in all_category_fields if isinstance(item, dict) and item.get('field_key') == key), None)
                        
                        if field_obj:
                            section['fields'].append(field_obj)
                        else:
                            # 2. Ищем в custom_forms (с защитой от None)
                            data_custom_forms = section.get('custom_forms') or []
                            custom_field = next((item for item in data_custom_forms if isinstance(item, dict) and item.get('field_key') == key), None)
                            
                            # Добавляем в fields ТОЛЬКО если поле действительно найдено
                            if custom_field:
                                section['fields'].append(custom_field)

        order_information.json_forms = json_models_data
        order_information.save()

        return HttpResponse(status=204)


