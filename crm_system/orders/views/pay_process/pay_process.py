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
from datetime import datetime, timedelta
import json
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import Cast
from django.shortcuts import render
from profile_user.models import WorkersInfo
from django.db.models import Q, Value
from django.db.models.functions import Concat
from profile_user.models import StatusCategory
from orders.models import Orders, CreateServiceWork
from finance.models import FinanceHistoryInfo
from finance.models import CashAccount

# Данный класс отвечает за показ шаблона об оплате + регистрирует саму оплату в БД 
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowAndPayView(View):

    # Регистрирую саму оплату 
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Имя клиента
        name_client = request.POST.get('name_client')

        # Итоговая цена к оплате
        summary_price = request.POST.get('summary_price').replace("\xa0", '')
        print(summary_price)

        # Тип оплаты: (НАЛИЧНЫЕ / КАРТОЙ)
        selected_type_pay = request.POST.get('selected_type_pay')

        # Ид заказа (получаю)
        id_order = request.POST.get('id_order')

        try:
            # Получаю данные по заказу
            get_order = Orders.objects.get(user=request.user, id=id_order)

            # Получаю весь список оказанных работ, которые соединены с именно этим типом заказа
            get_all_services = CreateServiceWork.objects.filter(user=request.user, connected_id=id_order).order_by('service_was_created')
            str_of_services = ''
            # Через цикл делаю перечислением те услуги, которые связаны с этим заказом
            for service in get_all_services:
                str_of_services += f'{service.service_provided}, цена: {service.service_price} руб., '
            str_of_services+=f'Итого к оплате: {summary_price} руб., Оплата: {selected_type_pay}.'
            print(str_of_services)

            # Создание истории операции(финансовой) на внесение средств 
            create_finance_history = FinanceHistoryInfo.objects.create(user=request.user,
            type_of_operation=FinanceHistoryInfo.TypeOfOperation.INCOME, category_of_operation=FinanceHistoryInfo.CategoryOfOperation.COMPLETED_WORK,
            number_in_the_operation=summary_price, product_name=f'Ремонтная услуга по заказу №{get_order.id}', 
            supplier=name_client, comment=f'Оказание ремонтных услуг клиенту: {name_client}, устройство: {get_order.name_of_device}. Услуги: {str_of_services}')

            # Внесение денег в кассу:
            # На уровне F выражения меняю баланс в положительную сторону (так как продажа)
            CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') + summary_price)

            print('Финансовая операция оплаты прошла успешно!')
            # Возвращается пустой ответ с закрытием сайдбара
            response = HttpResponse(status=200)
            response.content = """
                <script>
                    // Закрываем оба сайдбара и обновляем интерфейс
                    document.getElementById('payment-drawer-container').innerHTML = '';
                    if (typeof closeOrderDrawer === 'function') { closeOrderDrawer(); }
                </script>
            """
            response['HX-Trigger'] = json.dumps({
                'refreshOrders': True,
            })
            return response

        except Exception as e:

            msg = f'Ошибка: {e}'
            print(msg)
            return HttpResponse(status=400)


