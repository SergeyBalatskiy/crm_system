from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.http import HttpResponse
from profile_user.models import FormsForOrder
from slugify import slugify
import json
from django.contrib import messages

# Класс, который позволяет создать новую форму
@method_decorator(login_required(), name='dispatch')
class CreateNewFormInCategory(TemplateView):
   
    # Тут будет мой HTML который я буду отображать для индивидуальной добавки формы
    create_individual_form = 'profile_user/create_form/create_individual_form.html'

    def get(self, request, *args, **kwargs):

        # Получаю тип заказа
        type_of_order_selected = request.GET.get("type_of_order_selected")
        
        # Получаю категорию где создают форму
        category = request.GET.get("category")
        print("Запросили на показ гет запросом:", type_of_order_selected, category)
        return render(request, self.create_individual_form, {'type_of_order_selected' : type_of_order_selected, 'category': category })

    def post(self, request, *args, **kwargs):

        # Выбранная категория
        category = request.POST.get('category')

        # Само название индивидуальной формы
        label = request.POST.get('label')

        # Чекбокс по поводу select
        checkbox1 = request.POST.get('checkbox1')
        # Чекбокс по поводу checkbox  
        checkbox2 = request.POST.get('checkbox2')
        # Чекбокс по поводу textarea
        checkbox3 = request.POST.get('checkbox3')

        if checkbox1:
            cur_type = 'text'
        if checkbox2:
            cur_type = 'checkbox'
        if checkbox3:
            cur_type = 'textarea'

        # Поле обязательно?
        is_required = request.POST.get('is_required')

        # Выбранный тип заказа
        type_of_order_selected = request.POST.get('type_of_order_selected')

        # Получаю обьект из БД
        order_information = FormsForOrder.objects.filter(type_of_order = type_of_order_selected, user = self.request.user).first()

        # Беру JSON определенного типа заказа и для удобства записываю в переменную
        json_models_data = order_information.json_forms

        for section in json_models_data.get('sections', []):
                    if section['id'] == category:
                        lst_for_add_category = section['custom_forms']
                        for custom_form in lst_for_add_category:
                            if custom_form['label'] == label:
                                messages.error(request, 'Название с такой формой уже существует!')
                                print('Сработал только этот блок!')
                                return render(request, self.create_individual_form, {'type_of_order_selected' : type_of_order_selected, 'category': category })
                        else:
                            try:
                                lst_for_add_category.append({'field_key' : f'custom-{slugify(label)}', 'label' : label, 'type' : cur_type, 'is_required' : is_required, 'order': len(lst_for_add_category)+1, 'custom_form' : 'True'})
                                order_information.json_forms = json_models_data
                                order_information.save()
                                # Для GET запроса
                                objects_show = category
                                args_for_get_trigger = {
                                "formCreated": {
                                    "objects_show": objects_show,
                                    "type_of_order_selected": type_of_order_selected
                                }
                            }
                                response = HttpResponse("")
                                response["HX-Trigger"] = json.dumps(args_for_get_trigger)
                                return response
                            except:
                                messages.error(request, 'Необходимо выбрать тип формы!')
                                return render(request, self.create_individual_form, {'type_of_order_selected' : type_of_order_selected, 'category': category })
                                 

