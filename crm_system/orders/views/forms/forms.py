from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from orders.models import Client
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.db.models.functions import Cast
from django.shortcuts import render, redirect
from django.db.models import Q
from profile_user.models import FormsForOrder
from orders.models import Orders
from finance.models import CashAccount, FinanceHistoryInfo
from django.db.models import F
from django.http import HttpResponse
from datetime import datetime
import json

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

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        context = {'sections' : section, 'current_type': type_of_order_selected}

        # ЕСЛИ запрос пришел конкретно от селекта
        if request.headers.get('HX-Target') == 'form-change':
            return render(request, 'orders/form_inner/form_inner.html', context)
        
        return render(request, 'orders/forms/forms.html', context)

    # Обработчик JSON поля, который будет записывать АКТУАЛЬНЫЕ все поля + В бд данные для фильтрации
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        try:
            # Получаю имя, телефон
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()

            # GET_or_CREATE - если обьекта нет, создаю и вношу в create_client
            client, create_client = Client.objects.get_or_create(name=name, phone=phone, user=request.user)
            # Отладка для себя
            if client:
                print(f'У нас новый клиент: {create_client}')

            # Если чекбокс отмечен, вернет True. Если не отмечен — False.
            important = 'important' in request.POST

            manager = request.POST.get('manager')

            # Получаю название модели (если оно есть)
            name_device = request.POST.get('model', '')

            # Если есть предоплата:
            prepay = request.POST.get('prepay')
            
            if prepay:
                prepay_amount = int(request.POST.get('prepay_amount').replace(' ', '').replace('\xa0', '').strip())
            else:
                prepay_amount = 0

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

            # Ну а этот список у меня для сохранения заявки на ремонт в саму БД (Orders > form_with_order_information)
            json_field_for_order = []

            # Сам словарь который хранит уже все поля
            order_dict = {}

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

                    # В этот словарь добавляю ключ по которому можно будет идентифицировать поле
                    client_info['id'] = 'client_info'
                    json_field_for_order.append(client_info)

                # ЗАПИСЫВАЮ В ДЕВАЙС ИНФО ВСЕ ПОЛЯ (ДАЖЕ ПУСТЫЕ И ТЕ КОТОРЫЕ ПРИШЛИ)
                if section['id'] == 'device_info':
                    for field in section.get('fields'):
                        key = field.get('field_key')

                        if key in request.POST:
                            device_info[key] = request.POST.get(key)
                        else:
                            device_info[key] = ''

                    # В этот словарь добавляю ключ по которому можно будет идентифицировать поле
                    device_info['id'] = 'device_info'
                    json_field_for_order.append(device_info)

                # ЗАПИСЫВАЮ В БОНУС ИНФОРМАТИОН ВСЕ ПОЛЯ (ДАЖЕ ПУСТЫЕ И ТЕ КОТОРЫЕ ПРИШЛИ)
                if section['id'] == 'bonus_information':
                    for field in section.get('fields'):
                        key = field.get('field_key')

                        if key in request.POST:
                            bonus_info[key] = request.POST.get(key)
                        else:
                            bonus_info[key] = ''

                    # В этот словарь добавляю ключ по которому можно будет идентифицировать поле
                    bonus_info['id'] = 'bonus_information'
                    json_field_for_order.append(bonus_info)

            # Вставляю в этот словарь следуюего вида данные: {'order_dict' : [{...}, {...}, {...}]}
            order_dict['order_dict'] = json_field_for_order

            Orders.objects.create(user = request.user, type_of_order = type_of_order_selected, manager = manager, client = client, 
            device_type = request.POST.get('type_of_device', ''), color_of_device = request.POST.get('color', ''),
            problem_with_device = request.POST.get('destroyed', ''), name_of_device = name_device,
            deadline = request.POST.get('deadline', None), form_with_order_information = order_dict, important = important,
            prepay = prepay_amount)

            if prepay_amount > 0:
                # На уровне F выражения меняю баланс в положительную сторону из-за предоплаты
                CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') + prepay_amount)

                # Получаю дату и время для дальнейшего использования в комментариях
                now = datetime.now()
                formatted_dmy = now.strftime('%d.%m.%Y')
                formatted_hm = now.strftime('%H:%M')
                
                # Сделал историю операции финансовой если идет предоплата:
                FinanceHistoryInfo.objects.create(user=request.user, 
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.INCOME, category_of_operation = FinanceHistoryInfo.CategoryOfOperation.OTHER,
                number_in_the_operation = prepay_amount, product_name = name_device,
                supplier = 'Предоплата', comment = f"Внесение предоплаты в размере: {prepay_amount}, за ремонт: {name_device}. Клиент: {name}. Дата проведения операции: {formatted_dmy}, в {formatted_hm}")   

            print('Ничего не вылетело, все работает! Сохранение произошло.')
            # Отвечаем клиенту: закрываем шторку и показываем уведомление
            response = HttpResponse(status=200)
            response['HX-Trigger'] = json.dumps({
                'closeOrderDrawer': True,
                'showToast': {
                    'level': 'success',
                    'message': 'Заказ успешно создан!'
                }
            })
            return response
    
        except Exception as e:
            msg = f'Возникла ошибка: {e}'
            print(msg)
            return HttpResponse(f'Возникла ошибка при создании заказа: {e}', status=400)