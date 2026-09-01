from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.models import FormsForOrder
from django.http import HttpResponse
import json

# Классовое представление удаления кастомной формы
@method_decorator(login_required(), name='dispatch')

class DeleteCustomForm(TemplateView):

    def post(self, request, *args, **kwargs):
        type_of_order_selected = request.POST.get('type_of_order_selected')
        objects_show = request.POST.get('objects_show')
        print("1111212", objects_show)

        # Безопасный парсинг JSON с формами на удаление
        raw_deleted_forms = request.POST.get('deleted_custom_forms', '[]')
        try:
            deleted_custom_forms = json.loads(raw_deleted_forms)
        except (json.JSONDecodeError, TypeError):
            deleted_custom_forms = []

        # Если пришел одиночный элемент строкой, оборачиваем в список
        if isinstance(deleted_custom_forms, str):
            deleted_custom_forms = [deleted_custom_forms]

        order_information = FormsForOrder.objects.filter(
            type_of_order=type_of_order_selected, 
            user=self.request.user
        ).first()

        if not order_information or not order_information.json_forms:
            return HttpResponse(status=400)
        
        json_models_data = order_information.json_forms

        for section in json_models_data.get('sections', []):
            if section.get('id') == objects_show:

                # Защита от None: если ключа нет или он None, используем дефолтные типы
                custom_forms = section.get('custom_forms') or []
                saved_hints = section.get('saved_hints') or {}

                for form_key_to_delete in deleted_custom_forms:
                    # 1. Удаляем форму из custom_forms через list comprehension
                    section['custom_forms'] = [
                        form for form in custom_forms 
                        if form_key_to_delete not in form.get('field_key', '')
                    ]

                    # 2. Безопасно удаляем автоответы из saved_hints
                    if isinstance(saved_hints, dict):
                        keys_to_remove = [
                            key for key in saved_hints 
                            if form_key_to_delete in key
                        ]
                        for key in keys_to_remove:
                            del saved_hints[key]
                            print('Удален автоответ:', key)

                # Сохраняем обновленный объект в БД
                order_information.json_forms = json_models_data
                order_information.save()
                
                # Формируем HTMX триггер
                args_for_get_trigger = {
                    "formCreated": {
                        "objects_show": objects_show,
                        "type_of_order_selected": type_of_order_selected
                    }
                }
                response = HttpResponse(status=204)
                response["HX-Trigger"] = json.dumps(args_for_get_trigger)
                return response

        return HttpResponse(status=200)


                        
    