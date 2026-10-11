from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Client
from services.forms import ServicesWorkForm
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
import json
from django.db.models.functions import Cast
from django.shortcuts import render, redirect
from django.db.models import Q
from profile_user.models import FormsForOrder

# Данный класс отвечает за обращение в БД за получением формы и вывод ее 
# актуальных обьектов (из информации о клиенте, устройстве, прочей информации
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowFormForOrder(View):

    def get(self, request, *args, **kwargs):

        # Получаю тип заказа
        # Если тип заказа не выбран, отдаю дефолт форму (ее только что открыли)
        type_of_order_selected = request.GET.get('type_of_order_selected', 'paid')

        # Отдаю актуальные формы
        get_forms = FormsForOrder.objects.filter(user=request.user, type_of_order=type_of_order_selected).first()
        section = get_forms.json_forms.get('sections')

        print(section)

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        context = {'sections' : section, 'current_type': type_of_order_selected}

        # ЕСЛИ запрос пришел конкретно от селекта
        if request.headers.get('HX-Target') == 'form-change':
            return render(request, 'orders/form_inner/form_inner.html', context)
        
        return render(request, 'orders/forms/forms.html', context)

    # Обработчик JSON поля, который будет записывать АКТУАЛЬНЫЕ все поля
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Получаю имя, телефон
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()

        # GET_or_CREATE - если обьекта нет, создаю и вношу в create_client
        client, create_client = Client.objects.get_or_create(name=name, phone=phone, user=request.user)
        # Отладка для себя
        if not client:
            print(f'У нас новый клиент: {create_client}')

        # Если чекбокс отмечен, вернет True. Если не отмечен — False.
        important = 'important' in request.POST

        # Если есть предоплата:
        prepay = request.POST.get('prepay')
        if prepay:
            prepay_amount = request.POST.get('prepay_amount')

        # Тип заказа:
        type_of_order_selected = request.POST.get('type_of_order_selected')

        # Получаю конкретный обьект формы (по типу заказа)
        get_json_forms = FormsForOrder.objects.filter(user=request.user, type_of_order=type_of_order_selected).first()

        # Список для инофрмации о клиенте
        client_info = {}
        # Список о информации устройства
        device_info = {}
        # Список о прочей информации
        bonus_info = {}

        # Ну а этот словарь у меня для сохранения заявки на ремонт в саму БД (Orders > form_with_order_information)
        json_field_for_order = {}

        sections = get_json_forms.json_forms.get('sections')

        # Получаю по каждому обьекту
        for section in sections:
            # ЗАПИСЫВАЮ В КЛИЕНТ ИНФО ВСЕ ПОЛЯ (ДАЖЕ ПУСТЫЕ И ТЕ КОТОРЫЕ ПРИШЛИ)
            if section['id'] == 'client_info':
                for field in section.get('fields'):
                    key = field.get('field_key')

                    if key in request.POST:
                        client_info[key] = request.POST.get(key)
                    else:
                        client_info[key] = ''

                json_field_for_order[section['id']] = client_info

            # ЗАПИСЫВАЮ В ДЕВАЙС ИНФО ВСЕ ПОЛЯ (ДАЖЕ ПУСТЫЕ И ТЕ КОТОРЫЕ ПРИШЛИ)
            if section['id'] == 'device_info':
                for field in section.get('fields'):
                    key = field.get('field_key')

                    if key in request.POST:
                        device_info[key] = request.POST.get(key)
                    else:
                        device_info[key] = ''

                json_field_for_order[section['id']] = device_info

            # ЗАПИСЫВАЮ В БОНУС ИНФОРМАТИОН ВСЕ ПОЛЯ (ДАЖЕ ПУСТЫЕ И ТЕ КОТОРЫЕ ПРИШЛИ)
            if section['id'] == 'bonus_information':
                for field in section.get('fields'):
                    key = field.get('field_key')

                    if key in request.POST:
                        bonus_info[key] = request.POST.get(key)
                    else:
                        bonus_info[key] = ''

                json_field_for_order[section['id']] = bonus_info

