import json
import ast
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from profile_user.models import FormsForOrder

""" Данное классовое представление отвечает за добавление, чтение, отображение, удаление форм из БД.
Тут же я еще добавил (для упрощения во взаимодействии) константу ALL_CRM_FIELDS.
Вы будете правы, если скажете, что этот файл перегружен таким огромным количеством взаимодействий!
Признаю, что лучше было бы разбить логику на более мелкие views-классовые представления! """

@method_decorator(login_required(), name='dispatch')
class FormsForOrdersEdit(TemplateView):

    template_name = 'profile_user/forms-editor.html'
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
        'bonus_information': [
            {'field_key': 'comment_of_order', 'label': 'Комментарий приемщика', 'type': 'textarea'},
            {'field_key': 'master', 'label': 'Мастер', 'type': 'select'},
            {'field_key': 'manager', 'label': 'Менеджер', 'type': 'select'},
            {'field_key': 'prepay', 'label': 'Предоплата', 'type': 'checkbox'},
            {'field_key': 'day_of_the_end', 'label': 'Крайний срок', 'type': 'select'},
            {'field_key': 'target_price', 'label': 'Ориентировочная цена', 'type': 'select'},
            {'field_key': 'urgently', 'label': 'Срочно', 'type': 'checkbox'},
        ]
    }

    # Здесь логика отображения уже актуальных форм (которые находятся в БД) + 
    # показ НЕ РЕЛЕВАНТНЫХ ФОРМ / показ "динамических" html (by HTMX)
    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request') == 'true':
            print("Вызвали гет запрос на отображение не релевантных форм")
            type_of_order_selected = request.GET.get('type_of_order_selected')
            objects_show = request.GET.get('objects_show')
            raw_active_fields = request.GET.get('active_fields', '[]')
            print('Пришел:', type_of_order_selected, objects_show)
            if objects_show and type_of_order_selected:
                print('Я получил objects_show и type_of_order_selected')
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

                order_information = FormsForOrder.objects.filter(
                    type_of_order=type_of_order_selected, 
                    user=self.request.user
                ).first()
                current_forms = []
                if order_information and order_information.json_forms:
                    for sec in order_information.json_forms.get('sections', []):
                        if isinstance(sec, dict) and str(sec.get('id')) == str(objects_show):
                            for field in sec.get('fields', []):
                                if isinstance(field, dict) and 'field_key' in field:
                                    current_forms.append(field['field_key'])
                irrelevant_forms = []
                crm_pool = (
                    self.ALL_CRM_FIELDS.get(objects_show) or 
                    self.ALL_CRM_FIELDS.get(int(objects_show) if str(objects_show).isdigit() else objects_show) or 
                    []
                )
                for obj_info in crm_pool:
                    if isinstance(obj_info, dict) and 'field_key' in obj_info:
                        if obj_info['field_key'] not in current_forms or obj_info['field_key'] in deleted_keys:
                            irrelevant_forms.append(obj_info)
                if order_information and order_information.json_forms:
                    for section in order_information.json_forms.get('sections', []):
                        if isinstance(section, dict) and str(section.get('id')) == str(objects_show):
                            custom_pool = section.get('custom_forms', [])
                            for custom_field in custom_pool:
                                if isinstance(custom_field, dict) and 'field_key' in custom_field:
                                    if custom_field['field_key'] not in current_forms:
                                        irrelevant_forms.append(custom_field)
                try:
                    active_keys = set(json.loads(raw_active_fields))
                except (json.JSONDecodeError, TypeError):
                    active_keys = set()

                # Фильтруем: убираем формы, ключи которых у пользователя УЖЕ есть на экране
                if active_keys and irrelevant_forms:
                    irrelevant_forms = [
                        f for f in irrelevant_forms 
                        if isinstance(f, dict) and f.get('field_key') not in active_keys]
                print(f'Отдаю ирелевантные формы: {irrelevant_forms}')
                return render(
                    request, 
                    self.individual_window_forms, 
                    {
                        'irrelevant_forms': irrelevant_forms, 
                        'objects_show': objects_show, 
                        'type_of_order_selected': type_of_order_selected
                    }
                )
            order_information = FormsForOrder.objects.filter(
                type_of_order=type_of_order_selected, 
                user=self.request.user
            ).first()
            return render(request, self.form_orders_file, {'form_order': order_information})
        message = "Вы еще не выбрали ни один тип заказов."
        return render(request, self.template_name, {'message': message})
    
    # Здесь, пожалуй, самый сложный участок. Тут написана логика удаления, добавления, изменения порядка
    # форм в БД
    def post(self, request, *args, **kwargs):
        # Если пришли ключи для нового единого обработчика (сортировка, удаление или добавление)
        if any(key in request.POST for key in ['fields_order', 'list_deleted_forms', 'list_added_forms']):
            return self._delete_selected_forms(request)
        # Старая логика (если 'ordered_keys' отправляется из другого места)
        if 'ordered_keys' in request.POST:
            return self._save_fields_order(request)
        # Логика для одиночного добавления / выбора из модального окна
        objects_show = request.POST.get('objects_show')
        selected_forms = request.POST.getlist('selected_forms')
        type_of_order_selected = request.POST.get('type_of_order_selected')
        add_empty_slot = request.POST.get('add_empty_slot')
        if objects_show and type_of_order_selected:
            order_information = FormsForOrder.objects.filter(
                type_of_order=type_of_order_selected, 
                user=self.request.user
            ).first()
            if not order_information or not order_information.json_forms:
                return render(request, self.template_name)
            for section in order_information.json_forms.get('sections', []):
                if str(section.get('id')) == str(objects_show):
                    forms_list = section.get('fields', [])
                    custom_pool = section.get('custom_forms', [])
                    saved_hints = section.get('saved_hints', {})
                    for key in selected_forms:
                        if any(isinstance(f, dict) and f.get('field_key') == key for f in forms_list):
                            continue
                        standard_field = next(
                            (item for item in (self.ALL_CRM_FIELDS.get(objects_show) or []) if item.get('field_key') == key), 
                            None
                        )
                        field_hints = saved_hints.get(key, [])
                        new_field_data = None
                        if standard_field:
                            new_field_data = {
                                'label': standard_field['label'],
                                'field_key': standard_field['field_key'],
                                'type': standard_field['type'],
                                'hints': field_hints
                            }
                        else:
                            custom_field = next((item for item in custom_pool if item.get('field_key') == key), None)
                            if custom_field:
                                new_field_data = {
                                    'label': custom_field['label'],
                                    'field_key': custom_field['field_key'],
                                    'type': custom_field['type'],
                                    'hints': field_hints or custom_field.get('hints', []),
                                    'custom_form': True
                                }
                                section['custom_forms'] = [f for f in custom_pool if f.get('field_key') != key]
                        if new_field_data:
                            empty_slot_idx = next(
                                (i for i, f in enumerate(forms_list) if isinstance(f, dict) and f.get('field_key') == 'empty_place_for_add'),
                                None
                            )
                            if empty_slot_idx is not None:
                                forms_list[empty_slot_idx] = new_field_data
                            else:
                                forms_list.append(new_field_data)
                    if add_empty_slot and not any(isinstance(f, dict) and f.get('field_key') == 'empty_place_for_add' for f in forms_list):
                        forms_list.append({
                            'field_key': 'empty_place_for_add',
                            'label': 'Добавить поле +',
                            'type': '',
                            'hints': []
                        })
                    for idx, item in enumerate(forms_list, start=1):
                        if isinstance(item, dict):
                            item['order'] = idx
                    section['fields'] = forms_list
                    break
            order_information.save()
            return render(request, self.form_orders_file, {'form_order': order_information})
        return render(request, self.template_name)

    # Изменение порядка форм (сортировка) + добавление/удаление
    def _delete_selected_forms(self, request):
            json_string_forms = request.POST.get('list_deleted_forms', '{}')
            json_added_forms = request.POST.get('list_added_forms', '{}')
            raw_fields_order = request.POST.get('fields_order', '{}')
            try:
                forms_to_add = json.loads(json_added_forms)
            except (json.JSONDecodeError, TypeError):
                forms_to_add = {}
            try:
                forms_to_delete = json.loads(json_string_forms)
            except (json.JSONDecodeError, TypeError):
                forms_to_delete = {}
            try:
                sorted_orders = json.loads(raw_fields_order)
            except (json.JSONDecodeError, TypeError):
                sorted_orders = {}
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
                category_id = str(section.get('id', ''))
                sec_type = str(section.get('type') or section.get('code') or '')

                # ---- УДАЛЕНИЕ форм ----
                keys_to_delete = forms_to_delete.get(category_id) or forms_to_delete.get(sec_type) or []
                if keys_to_delete:
                    current_fields = section.get('fields', []) or []
                    new_fields_list = []
                    if 'custom_forms' not in section or not isinstance(section['custom_forms'], list):
                        section['custom_forms'] = []
                    for field in current_fields:
                        if isinstance(field, dict):
                            f_key = field.get('field_key')
                            if f_key in keys_to_delete:
                                if field.get('custom_form'):
                                    section['custom_forms'] = [
                                        cf for cf in section['custom_forms'] 
                                        if isinstance(cf, dict) and cf.get('field_key') != f_key
                                    ]
                                    section['custom_forms'].append(field)
                            else:
                                new_fields_list.append(field)
                    section['fields'] = new_fields_list

                # ---- ДОБАВЛЕНИЕ новых форм ----
                keys_to_add = forms_to_add.get(category_id) or forms_to_add.get(sec_type) or []
                if keys_to_add:
                    all_category_fields = self.ALL_CRM_FIELDS.get(category_id) or self.ALL_CRM_FIELDS.get(sec_type) or []
                    current_fields = section.get('fields', []) or []
                    existing_keys = [f.get('field_key') for f in current_fields if isinstance(f, dict) and f.get('field_key')]
                    saved_hints = section.get('saved_hints', {})
                    for key in keys_to_add:
                        if key not in existing_keys and key not in ['empty_for_add', 'empty_place_for_add']:
                            added_field = None
                            if (field_obj := next((item for item in all_category_fields if isinstance(item, dict) and item.get('field_key') == key), None)):
                                added_field = dict(field_obj)
                            else:
                                data_custom_forms = section.get('custom_forms') or []
                                custom_field = next((item for item in data_custom_forms if isinstance(item, dict) and item.get('field_key') == key), None)
                                if custom_field:
                                    added_field = dict(custom_field)
                            if added_field:
                                if key in saved_hints:
                                    added_field['hints'] = saved_hints[key]
                                section['fields'].append(added_field)

                # ---- Cортировка форм ----
                new_order_keys = sorted_orders.get(category_id) or sorted_orders.get(sec_type)
                if new_order_keys:
                    current_fields_map = {
                        f.get('field_key'): f 
                        for f in section.get('fields', []) 
                        if isinstance(f, dict) and f.get('field_key')
                    }
                    reordered_fields = []
                    for key in new_order_keys:
                        if key in current_fields_map:
                            reordered_fields.append(current_fields_map[key])
                        elif key in ['empty_for_add', 'empty_place_for_add']:
                            reordered_fields.append({
                                'field_key': 'empty_for_add',
                                'label': 'empty',
                                'type': '',
                                'is_required': False,
                                'hints': []
                            })
                    section['fields'] = reordered_fields

                # ---- Удаление ненужных (лишних) "Пустышек" ----
                clean_fields = [f for f in section.get('fields', []) if f is not None]
                while clean_fields and isinstance(clean_fields[-1], dict) and clean_fields[-1].get('field_key') in ['empty_for_add', 'empty_place_for_add']:
                    clean_fields.pop()
                section['fields'] = clean_fields

                # ---- Пересчет order ----
                for idx, f in enumerate(section.get('fields', []), start=1):
                    if isinstance(f, dict):
                        f['order'] = idx

            # 3. Сохранение изменений в БД
            order_information.json_forms = json_models_data
            order_information.save()
            return HttpResponse(status=204)