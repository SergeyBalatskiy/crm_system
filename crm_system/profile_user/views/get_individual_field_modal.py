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
        
        # Получаю обьект из БД
        order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

        for section in order_information.json_forms.get('sections', []):
           if section["id"] == category:
               fields = section.get("fields", [])
               for one_field in fields:
                   if field_key in one_field["field_key"]:
                       return render(request, self.edit_individual_form, {"individual_form": one_field, "category" : category, "type_of_order_selected" : type_of_order_selected})

    def post(self, request, *args, **kwargs):

        # Выбранная категория
        category = request.POST.get('category')

        # Само название индивидуальной формы
        field_key = request.POST.get('field_key')

        # Выбранный тип заказа
        type_of_order_selected = request.POST.get('type_of_order_selected')

        # Все подсказки которые были присланы
        hints_list = request.POST.getlist('hints')
        # Выводит : ['Телефон', 'Ноутбук', 'Планшет', 'Компьютер']

        while '' in hints_list:
            hints_list.remove('')

        # Получаю обьект из БД
        order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

        # Беру JSON определенного типа заказа и для удобства записываю в переменную
        json_models_data = order_information.json_forms

        # Дописать логику редактирования (перезаписывания) подсказок
        for section in json_models_data.get('sections', []):
                    if section['id'] == category:
                        for field in section.get('fields', []):
                            if field_key in field['field_key']:
                                field['hints'] = hints_list
                                # Сохраняю сам новый порядок (после изменения списка)
                                order_information.json_forms = json_models_data
                                order_information.save()
                                return HttpResponse(status=204)
