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
import re
from datetime import datetime
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
from num2words import num2words


# Отвечает за написание Имени и Первой буквы фамилии "Игорь Л."
def format_initials(initials):

    if not initials:
        return ""

    index = initials.index(" ")
    format_int = initials[0 : index + 2]
    return format_int + "."


# Отвечает за превращение числа в пропись
def number_in_words(number):
    if not number:
        return ""

    number_text = num2words(number, lang="ru")

    return number_text.capitalize()


# Словарь, где ключ это триггер-переменная, значение это данные, которые нужно вставить
DOCUMENT_VARIABLES = {
    "<НомерЗаказа>": lambda order, services, **kwargs: str(order.id),
    "<ДатаВыдачи>": lambda order, services, **kwargs: datetime.now().strftime(
        "%d.%m.%Y, %H:%M"
    ),
    "<ТипЗаказа>": lambda order, services, **kwargs: str(
        getattr(order, "type_of_order", "")
    ),
    # Клиент
    "<Контрагент>": lambda order, services, **kwargs: str(
        getattr(order, "client.name", "")
    ),
    "<НомерКонтрагента>": lambda order, services, **kwargs: str(
        getattr(order, "client.phone", "")
    ),
    "<КонтрагентСокр>": lambda order, services, **kwargs: format_initials(
        getattr(order, "client.name", "")
    ),
    # Устройство
    "<Марка>": lambda order, services, **kwargs: str(
        getattr(order, "device_company", "")
    ),
    "<Модель>": lambda order, services, **kwargs: str(
        getattr(order, "name_of_device", "")
    ),
    "<Неисправность>": lambda order, services, **kwargs: str(
        getattr(order, "problem_with_device", "")
    ),
    # Прочее
    "<Вердикт>": lambda order, services, **kwargs: str(
        getattr(order, "problem_with_device", "")
    ),
    # Сервисный центр
    "<Менеджер>": lambda order, services, **kwargs: str(getattr(order, "manager", "")),
    "<МенеджерСокр>": lambda order, services, **kwargs: format_initials(
        getattr(order, "manager", "")
    ),
    "<НазваниеОрганизации>": lambda order, services, company_inf: str(
        getattr(company_inf, "name_service", "")
    ),
    "<АдресОрганизации>": lambda order, services, company_inf: str(
        getattr(company_inf, "address", "")
    ),
    # Финансы
    "<СуммаЧека>": lambda order, services, **kwargs: (
        str(sum(s.service_price for s in services)) if services else "0"
    ),
    "<Скидка>": lambda order, services, **kwargs: str(getattr(order, "discount", 0)),
    "<ИтогоЦена>": lambda order, services, **kwargs: (
        str(sum(s.service_price for s in services) - order.discount)
    ),
    "<ВсегоПозиций>": lambda order, services, **kwargs: str(
        len(services) if services else 0
    ),
    "<ИтогоПрописьюТекстом>": lambda order, services, **kwargs: number_in_words(
        sum(s.service_price for s in services) - order.discount
    ),
}


# Данный класс отвечает за показ шаблона об оплате + регистрирует саму оплату в БД
@method_decorator([login_required, never_cache], name="dispatch")
class ShowAndPayView(View):

    # Добавляю новую функцию которая отвечает за замену "переменных" в момент "показа" нашего актуального
    # шаблона документа "Акт выполненных работ":
    # Здесь передается: шаблон показываемого документа \ данные заказа \ все работы, прикрепленные к заказу \
    # Информация о сервисе
    def replace_fields_for_document(template_html, order, services, company_inf):

        # Нахожу то самое место с названием оказываемой услуги и говорим что после написания нужно переносить
        # на новую строку
        row_pattern = r"(<tr[^>]*>.*?<НазваниеОказываемойУслуги>.*?</tr>)"
        match = re.search(row_pattern, template_html, re.DOTALL | re.IGNORECASE)

        # Если есть такое место:
        if match and services:
            single_row_template = match.group(1)
            generated_rows = ""

            # Данный цикл отвечает ТОЛЬКО за создание поля услуг (всей строки от номера до суммы итоговой)
            summary_price = 0
            for idx, service in enumerate(services, start=1):
                # Используя enumerate я прохожусь по списку работ, записываю ее номер (порядковый) + беру само название
                # чтобы вставлять потом в саму строку (одну)
                row_html = single_row_template
                row_html = row_html.replace("<Номер>", str(idx))
                row_html = row_html.replace(
                    "<КодДетали>", str(getattr(services, "detail_id", ""))
                )
                row_html = row_html.replace(
                    "<НазваниеОказываемойУслуги>", str(services.service_provided)
                )
                row_html = row_html.replace(
                    "<Гарантия>", str(getattr(services, "days_of_garanty", "0"))
                )
                row_html = row_html.replace(
                    "<СтоимостьУслуги>", str(services.service_price)
                )
                summary_price += services.service_price
                row_html = row_html.replace("<СуммаУслуг>", str(summary_price))
                generated_rows += row_html

            # Здесь я заменяю строку с переменными на отформатированную
            template_html = template_html.replace(single_row_template, generated_rows)

        # Для переменной и ее значения из списка элементов словаря:
        for tag, get_value_func in DOCUMENT_VARIABLES.items():
            # Если триггер-переменная в самом шаблоне документа:
            if tag in template_html:
                try:
                    # Вызов лямбда-функции с передачей данных и отдачей от нее самого результата
                    replacement_value = get_value_func(order, services, company_inf)
                    # Вставка полученного результата от replacement_value
                    template_html = template_html.replace(tag, str(replacement_value))
                except Exception:
                    # Если у какого-то поля нет данных, просто заменяем на пустую строку, чтобы тег не мозолил глаза
                    template_html = template_html.replace(tag, "")

        return template_html

    # Регистрирую саму оплату
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Имя клиента
        name_client = request.POST.get("name_client")

        # Итоговая цена к оплате
        summary_price = request.POST.get("summary_price").replace("\xa0", "")
        print(summary_price)

        # Тип оплаты: (НАЛИЧНЫЕ / КАРТОЙ)
        selected_type_pay = request.POST.get("selected_type_pay")

        # Ид заказа (получаю)
        id_order = request.POST.get("id_order")

        try:
            # Получаю данные по заказу
            get_order = Orders.objects.get(user=request.user, id=id_order)

            # Получаю весь список оказанных работ, которые соединены с именно этим типом заказа
            get_all_services = CreateServiceWork.objects.filter(
                user=request.user, connected_id=id_order
            ).order_by("service_was_created")
            str_of_services = ""
            # Через цикл делаю перечислением те услуги, которые связаны с этим заказом
            for service in get_all_services:
                str_of_services += (
                    f"{service.service_provided}, цена: {service.service_price} руб., "
                )
            str_of_services += (
                f"Итого к оплате: {summary_price} руб., Оплата: {selected_type_pay}."
            )
            print(str_of_services)

            # Создание истории операции(финансовой) на внесение средств
            create_finance_history = FinanceHistoryInfo.objects.create(
                user=request.user,
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.INCOME,
                category_of_operation=FinanceHistoryInfo.CategoryOfOperation.COMPLETED_WORK,
                number_in_the_operation=summary_price,
                product_name=f"Ремонтная услуга по заказу №{get_order.id}",
                supplier=name_client,
                comment=f"Оказание ремонтных услуг клиенту: {name_client}, устройство: {get_order.name_of_device}. Услуги: {str_of_services}",
            )

            # Внесение денег в кассу:
            # На уровне F выражения меняю баланс в положительную сторону (так как продажа)
            CashAccount.objects.filter(user=request.user).update(
                money_balance=F("money_balance") + summary_price
            )

            print("Финансовая операция оплаты прошла успешно!")

            # После финансовой операции нужно сделать так, чтобы вызывалась функция на печать шаблона
            ...

            # Возвращается пустой ответ с закрытием сайдбара
            response = HttpResponse(status=200)
            response.content = """
                <script>
                    // Закрываем оба сайдбара и обновляем интерфейс
                    document.getElementById('payment-drawer-container').innerHTML = '';
                    if (typeof closeOrderDrawer === 'function') { closeOrderDrawer(); }
                </script>
            """
            response["HX-Trigger"] = json.dumps(
                {
                    "refreshOrders": True,
                }
            )
            return response

        except Exception as e:

            msg = f"Ошибка: {e}"
            print(msg)
            return HttpResponse(status=400)
