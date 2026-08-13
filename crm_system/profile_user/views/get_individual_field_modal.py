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
class EditIndividualCenterForm(TemplateView):
   
    # Тут будет мой HTML который я буду отображать для индивидуальной настройки формы
    edit_individual_form = 'profile_user/edit_form/edit_individual_form.html'

    def get(self, request, *args, **kwargs):
        type_of_order_selected = request.GET.get("type_of_order_selected")
        section_id = request.GET.get("section_id")
        field_key = request.GET.get("field_key")
        category = request.GET.get("category")
        
        # 1. Считываем русское название из GET-запроса (если нет — ставим field_key как запасной вариант)
        field_label = request.GET.get("field_label") or field_key

        # Получаю объект из БД
        order_information = FormsForOrder.objects.filter(
            type_of_order=type_of_order_selected, 
            user=self.request.user
        ).first()

        target_field = None

        # 2. Ищем поле в структуре JSON
        if order_information and order_information.json_forms:
            sections = order_information.json_forms.get('sections', [])
            for section in sections:
                if str(section.get("id")) == str(category):
                    fields = section.get("fields", [])
                    for one_field in fields:
                        if isinstance(one_field, dict) and one_field.get("field_key") == field_key:
                            target_field = one_field
                            break

        # 3. ФОЛЛБЕК: Если поля нет в БД (новое/несохраненное поле с фронтенда)
        if not target_field:
            target_field = {
                "field_key": field_key,
                "label": field_label,  # <-- Теперь берется "Телеграм", "Комплектация" и т.д.
                "hints": []
            }

        # 4. ГАРАНТИРОВАННЫЙ RETURN
        return render(
            request, 
            self.edit_individual_form, 
            {
                "individual_form": target_field, 
                "category": category, 
                "type_of_order_selected": type_of_order_selected
            }
        )
            
    def post(self, request, *args, **kwargs):
        category = request.POST.get('category')
        field_key = request.POST.get('field_key')
        type_of_order_selected = request.POST.get('type_of_order_selected')
        field_label = request.POST.get('field_label')
        print(field_label)
        # Очищаем пустые строки через list comprehension
        hints_list = [hint for hint in request.POST.getlist('hints') if hint.strip()]

        # Получаем объект из БД
        order_information = FormsForOrder.objects.filter(
            type_of_order=type_of_order_selected, 
            user=self.request.user
        ).first()

        if not order_information or not order_information.json_forms:
            return HttpResponse("Форма не найдена", status=400)

        json_models_data = order_information.json_forms
        sections = json_models_data.get('sections', [])
        
        field_found = False

        # 1. Пробуем найти и обновить существующее поле
        for section in sections:
            if str(section.get('id')) == str(category):
                fields = section.get('fields', [])
                for field in fields:
                    if isinstance(field, dict) and field.get('field_key') == field_key:
                        field['hints'] = hints_list
                        if field_label:
                            field['label'] = field_label 
                        field_found = True
                        break

                # 2. Если поля еще НЕТ в БД (добавлено на фронте) — создаем его в этой секции
                if not field_found:
                    new_field = {
                        "field_key": field_key,
                        "label": field_label, # или дефолтное название
                        "hints": hints_list,
                        "order": len(fields) + 1
                    }
                    fields.append(new_field)
                    field_found = True
                break

        # 3. Сохраняем измененный JSON
        order_information.json_forms = dict(json_models_data)
        order_information.save(update_fields=['json_forms'])

        # 4. ГАРАНТИРОВАННЫЙ RETURN (больше никаких None!)
        return HttpResponse(status=200)