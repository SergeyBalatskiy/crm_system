import json
import ast
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from profile_user.models import FormsForOrder

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
                print(irrelevant_forms)
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

    def post(self, request, *args, **kwargs):
        if 'ordered_keys' in request.POST:
            return self._save_fields_order(request)
        
        if 'list_deleted_forms' in request.POST:
            return self._delete_selected_forms(request)
        
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

                    # Обработка выбора новых форм из панели/модалки
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
                            # Проверяем наличие пустого слота-заглушки для замещения
                            empty_slot_idx = next(
                                (i for i, f in enumerate(forms_list) if isinstance(f, dict) and f.get('field_key') == 'empty_place_for_add'),
                                None
                            )
                            if empty_slot_idx is not None:
                                forms_list[empty_slot_idx] = new_field_data
                            else:
                                forms_list.append(new_field_data)

                    # Явное добавление пустого слота справа по кнопке
                    if add_empty_slot and not any(isinstance(f, dict) and f.get('field_key') == 'empty_place_for_add' for f in forms_list):
                        forms_list.append({
                            'field_key': 'empty_place_for_add',
                            'label': 'Добавить поле +',
                            'type': '',
                            'hints': []
                        })

                    # Автопересчет порядка от 1 до N
                    for idx, item in enumerate(forms_list, start=1):
                        if isinstance(item, dict):
                            item['order'] = idx

                    section['fields'] = forms_list
                    break

            order_information.save()
            return render(request, self.form_orders_file, {'form_order': order_information})
        
        return render(request, self.template_name)

    def _save_fields_order(self, request):
        section_id = request.POST.get('section_id')
        type_of_order = request.POST.get('type_of_order_selected')
        
        raw_keys = request.POST.getlist('ordered_keys') or request.POST.get('ordered_keys')
        
        ordered_keys = []
        if isinstance(raw_keys, list) and len(raw_keys) > 0 and str(raw_keys[0]).startswith('['):
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

            category_id = str(section.get('id'))

            current_fields = section.get('fields', []) or []
            existing_hints_map = {
                f.get('field_key'): f.get('hints', []) 
                for f in current_fields 
                if isinstance(f, dict) and f.get('field_key')
            }

            for cf in section.get('custom_forms', []) or []:
                if isinstance(cf, dict) and cf.get('field_key'):
                    if cf.get('field_key') not in existing_hints_map or not existing_hints_map[cf.get('field_key')]:
                        existing_hints_map[cf.get('field_key')] = cf.get('hints', [])

            keys_to_delete = forms_to_delete.get(category_id) or forms_to_delete.get(int(category_id) if category_id.isdigit() else category_id) or []

            # --- УДАЛЕНИЕ ЭЛЕМЕНТОВ ---
            if keys_to_delete:
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

            # --- ДОБАВЛЕНИЕ ЭЛЕМЕНТОВ ---
            keys_to_add = forms_to_add.get(category_id) or forms_to_add.get(int(category_id) if category_id.isdigit() else category_id) or []

            if keys_to_add:
                all_category_fields = self.ALL_CRM_FIELDS.get(category_id) or self.ALL_CRM_FIELDS.get(int(category_id) if category_id.isdigit() else category_id) or []
                
                current_fields = section.get('fields', []) or []
                existing_keys = [f.get('field_key') for f in current_fields if isinstance(f, dict) and 'field_key' in f]
                saved_hints = section.get('saved_hints', {})

                for key in keys_to_add:
                    if key not in existing_keys:
                        added_field = None
                        field_obj = next((item for item in all_category_fields if isinstance(item, dict) and item.get('field_key') == key), None)
                        
                        if field_obj:
                            added_field = dict(field_obj)
                        else:
                            data_custom_forms = section.get('custom_forms') or []
                            custom_field = next((item for item in data_custom_forms if isinstance(item, dict) and item.get('field_key') == key), None)
                            if custom_field:
                                added_field = dict(custom_field)

                        if added_field:
                            if key in saved_hints:
                                added_field['hints'] = saved_hints[key]

                            empty_slot_idx = next(
                                (i for i, f in enumerate(section['fields']) if isinstance(f, dict) and f.get('field_key') == 'empty_place_for_add'),
                                None
                            )
                            if empty_slot_idx is not None:
                                section['fields'][empty_slot_idx] = added_field
                            else:
                                section['fields'].append(added_field)

            # Пересчет order после всех изменений в секции
            for idx, f in enumerate(section.get('fields', []), start=1):
                if isinstance(f, dict):
                    f['order'] = idx

        order_information.json_forms = json_models_data
        order_information.save()

        return HttpResponse(status=204)