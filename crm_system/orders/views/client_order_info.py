from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Client
from orders.models import Orders
from services.forms import ServicesWorkForm
from finance.models import CashAccount, FinanceHistoryInfo
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from datetime import datetime, timedelta
import json
from django.db.models.functions import Cast
from django.shortcuts import render
from django.db.models import Q, Value
from django.utils import timezone
from django.db.models.functions import Concat
from profile_user.models import FormsForOrder

# Данный класс отвечает за показ конкретной информации о клиенте (о заказе)
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowClientOrder(View):

    # Отвечает за показ уже созданной заявки о клиенте
    def get(self, request, *args, **kwargs):
        get_id_order = request.GET.get('get_id_order')
        get_order = Orders.objects.filter(user = request.user, id=get_id_order).first()

        # Получаю действующую форму из Базы данных
        get_original_form = FormsForOrder.objects.filter(user=request.user).first()
        sections = get_original_form.json_forms.get('sections', [])

        # Получаю уже введенные данные из созданной заявки в базе данных
        saved_data = get_order.form_with_order_information.get('order_dict')
        # "Упаковываю" каждые из элементов в словарь(чтобы можно было потом просто достать)
        saved_map = {block['id']: block for block in saved_data}

        # Прохожусь индивидуально по каждому обьекту из формы из базы данных (актуальной)
        for section in sections:
            # После того как взял обьект - мне нужно у этого обьекта запомнить айди его 
            sec_id = section.get('id')
            # Получаю именно обьект с уже введенными данными благодаря айдишнику из БД!
            sec_saved_values = saved_map.get(sec_id, [])
            # Здесь проходит логика записывания введенных данных из полученных форм в ключ (данные записываются в как бы основной
            # JSON (главный, который имеет предварительно пустое поле, и это поле в дальнейшем заполняется!)
            for field in section.get('fields'):
                f_key = field.get('field_key')
                field['value'] = sec_saved_values.get(f_key)

        print(sections)
        print()
        print(get_order)

        context = {
            'get_order' : get_order,
            'sections' : sections,
            'current_type' : get_order.type_of_order,
        }
        return render(request, 'orders/show_getted_order/show_getted_form.html', context)

    # Отвечает за принятие каких-либо изменений(и их сохранение) в заявке
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        try:
            # Получаю имя, телефон
            name = request.POST.get('name', '').strip()

            # Благодаря этому айди получаю индивидуальный код заказа
            get_id_order = request.GET.get('get_id_order')

            # Если чекбокс отмечен, вернет True. Если не отмечен — False.
            is_urgently = 'urgently' in request.POST

            # Получаю менеджера
            manager = request.POST.get('manager')

            # Получаю название модели устройства (если оно есть)
            name_device = request.POST.get('model', '')

            # Если есть предоплата: (думаю что проверку того что предоплата была изменена, нужно проверять непосредственно через JS)
            # Если сумма была изменена, то даем ей записаться. Если нет - значит во время оправки запроса обнуляем.
            prepay = 'prepay' in request.POST

            if prepay:
                prepay_amount = int(request.POST.get('prepay_amount').replace(' ', '').replace('\xa0', '').strip())
            else:
                prepay_amount = 0

            # Тип заказа:
            type_of_order = request.GET.get('type_of_order')

            # Получаю конкретный обьект формы (по типу заказа)
            get_json_forms = FormsForOrder.objects.filter(user=request.user, type_of_order=type_of_order).first()

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

            # Получаю "оригинальные секции" из БД JSONfields (из PROFILE_USER > MODELS > FormsForOrder)
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

            # Вот это надо обновить!
            # Здесь должен быть гет ор креате и сохранение
            # Получаю обьект на обновление данных в нем
            order_to_update = Orders.objects.select_for_update().filter(user=request.user, id=get_id_order).first()

            print('Тут все норм 1')
            order_to_update.manager = manager
            order_to_update.device_type = request.POST.get('type_of_device', '')
            order_to_update.color_of_device = request.POST.get('color', '')
            order_to_update.name_of_device = request.POST.get('model', '')
            order_to_update.problem_with_device = request.POST.get('destroyed', '')
            order_to_update.deadline = request.POST.get('deadline', None)
            print('Тут все норм 2')
            order_to_update.form_with_order_information = order_dict
            order_to_update.important = is_urgently

            # Думаю что тут можно добавить проверку формата: была ли предоплата раньше?
            # Если предоплата (сам тумблер) в положении ОФФ и предоплата в базе данных была раньше:
            # Значит мы передумали делать предоплату, и ее нужно убрать!
            if not prepay and order_to_update.prepay > 0:
                # Здесь просто запоминаю саму сумму предоплаты чтобы потом удалить
                saved_count_prepay = order_to_update.prepay
                order_to_update.prepay = 0
                # На уровне F выражения меняю баланс в отрицательную сторону из-за убирания
                CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') - saved_count_prepay)

                # Получаю дату и время для дальнейшего использования в комментариях
                now = datetime.now()
                formatted_dmy = now.strftime('%d.%m.%Y')
                formatted_hm = now.strftime('%H:%M')
                
                # Сделал историю операции финансовой если идет убирание предоплаты:
                FinanceHistoryInfo.objects.create(user=request.user, 
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.OUTCOME, category_of_operation = FinanceHistoryInfo.CategoryOfOperation.OTHER,
                number_in_the_operation = saved_count_prepay, product_name = name_device,
                supplier = 'Отмена предоплаты', comment = f"Отмена предоплаты в размере: {saved_count_prepay}, за: {name_device}. Клиент: {name}. Дата проведения операции: {formatted_dmy}, в {formatted_hm}")   
                
            if prepay_amount > 0:
                order_to_update.prepay = order_to_update.prepay+prepay_amount
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
                supplier = 'Предоплата', comment = f"Дополнительное внесение предоплаты в размере: {prepay_amount}, за: {name_device}. Клиент: {name}. Дата проведения операции: {formatted_dmy}, в {formatted_hm}")   

            order_to_update.save()

            print('Ничего не вылетело, все работает! Сохранение произошло.')

            # Отвечаем клиенту: закрываем шторку и показываем уведомление
            response = HttpResponse(status=200)
            response['HX-Trigger'] = json.dumps({
                'closeOrderDrawer': True,
                'showToast': {
                    'level': 'success',
                    'message': 'Заказ успешно обновлен!'
                }
            })
            return response
    
        except Exception as e:
            msg = f'Возникла ошибка: {e}'
            print(msg)
            return HttpResponse(f'Возникла ошибка при создании заказа: {e}', status=400)