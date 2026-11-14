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
from num2words import num2words
import re
from django.db.models import Sum
from django.db.models.functions import Cast
from django.shortcuts import render
from profile_user.models import WorkersInfo
from django.db.models import Q, Value
from django.db.models.functions import Concat
from orders.models import Orders, CreateServiceWork
from profile_user.models import DocumentInformation, ServiceInfo


# Отвечает за написание Имени и Первой буквы фамилии "Игорь Л."
def format_initials(initials):

    if not initials:
        return ""
    elif " " not in initials:
        return initials

    index = initials.index(" ")
    format_int = initials[0 : index + 2]
    return format_int + "."


# Отвечает за превращение числа в пропись
def number_in_words(number):
    if not number:
        return "Ноль"

    number_text = num2words(number, lang="ru")
    return number_text.capitalize()


# Словарь, где ключ это триггер-переменная, значение это данные, которые нужно вставить
DOCUMENT_VARIABLES = {
    # Прочее
    "<ПричинаОтказа>": lambda order=None, services=None, company_inf=None, **kwargs: kwargs.get(
        "reason_for_refusal", ""
    ),
    "<Рекомендации>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "problem_with_device", "")
    ),
    "<НомерЗаказа>": lambda order, services=None, company_inf=None, **kwargs: str(
        order.id
    ),
    "<ДатаВыдачи>": lambda order, services=None, company_inf=None, **kwargs: datetime.now().strftime(
        "%d.%m.%Y, %H:%M"
    ),
    "<ТипЗаказа>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "type_of_order", "")
    ),
    # Клиент
    "<Контрагент>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order.client, "name", "")
        if hasattr(order, "client") and order.client
        else getattr(order, "name_client", "")
    ),
    "<НомерКонтрагента>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order.client, "phone", "")
        if hasattr(order, "client") and order.client
        else getattr(order, "phone_client", "")
    ),
    "<КонтрагентСокр>": lambda order, services=None, company_inf=None, **kwargs: format_initials(
        str(
            getattr(order.client, "name", "")
            if hasattr(order, "client") and order.client
            else getattr(order, "name_client", "")
        )
    ),
    # Устройство
    "<Марка>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "device_company", "")
    ),
    "<Модель>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "name_of_device", "")
    ),
    "<Неисправность>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "problem_with_device", "")
    ),
    "<Вердикт>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "problem_with_device", "")
    ),
    "<Комплектация>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "complectation", "")
    ),
    "<ВнешнийВид>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "visual", "")
    ),
    "<ОриентировочнаяСтоимостьРемонта>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "target_price", "")
    ),
    "<ОриентировочнаяДатаГотовности>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "day_of_the_end", "")
    ),
    "<КомментарийПриемщика>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "comment_of_order", "")
    ),
    # Сервисный центр
    "<Менеджер>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "manager", "")
    ),
    "<МенеджерСокр>": lambda order, services=None, company_inf=None, **kwargs: format_initials(
        str(getattr(order, "manager", ""))
    ),
    "<НазваниеОрганизации>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(company_inf, "name_service", "") if company_inf else ""
    ),
    "<АдресОрганизации>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(company_inf, "address", "") if company_inf else ""
    ),
    # Финансы
    "<Предоплата>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "prepay", 0)
    ),
    "<СуммаЧека>": lambda order, services=None, company_inf=None, **kwargs: (
        str(sum(s.service_price for s in services)) if services else "0"
    ),
    "<Скидка>": lambda order, services=None, company_inf=None, **kwargs: str(
        getattr(order, "discount", 0)
    ),
    "<ИтогоЦена>": lambda order, services=None, company_inf=None, **kwargs: (
        str(
            (sum(s.service_price for s in services) if services else 0)
            - (getattr(order, "discount", 0) or 0)
        )
    ),
    "<ВсегоПозиций>": lambda order, services=None, company_inf=None, **kwargs: str(
        len(services) if services else 0
    ),
    "<ИтогоПрописьюТекстом>": lambda order, services=None, company_inf=None, **kwargs: number_in_words(
        (sum(s.service_price for s in services) if services else 0)
        - (getattr(order, "discount", 0) or 0)
    ),
}


# Данный класс отвечает за показ документов и печать выбранного документа
@method_decorator([login_required, never_cache], name="dispatch")
class PrintSelectedDocument(View):

    # Берет из константы по ключу/значению уже готовое поле и записывает в документ
    # + записывает оказываемые услуги
    def replace_fields_for_document(
        template_html, order, services, company_inf, reason_for_refusal
    ):

        # Заменяю символы от tinyMCE на "<>"
        template_html = template_html.replace("&lt;", "<").replace("&gt;", ">")

        # Нахожу то самое место с названием оказываемой услуги и говорим что после написания нужно переносить
        # на новую строку
        row_pattern = r"(<tr[^>]*>(?:(?!<\/tr>).)*?<НазваниеОказываемойУслуги>(?:(?!<\/tr>).)*?<\/tr>)"
        match = re.search(row_pattern, template_html, re.DOTALL | re.IGNORECASE)

        # Если есть такое место:
        if match:
            # Находим его более точно
            single_row_template = match.group(1)
            generated_rows = ""

            # Проверяем, есть ли услуги?
            if services:

                # Данный цикл отвечает ТОЛЬКО за создание поля услуг (всей строки от номера до суммы итоговой)
                summary_price = 0
                for idx, service in enumerate(services, start=1):
                    # Используя enumerate я прохожусь по списку работ, записываю ее номер (порядковый) + беру само название
                    # чтобы вставлять потом в саму строку (одну)
                    row_html = single_row_template
                    row_html = row_html.replace("<Номер>", str(idx))
                    get_detail = getattr(service, "detail_id")
                    row_html = row_html.replace(
                        "<КодДетали>", str(get_detail if get_detail is not None else "")
                    )

                    row_html = row_html.replace(
                        "<НазваниеОказываемойУслуги>",
                        str(getattr(service, "service_provided", "")),
                    )
                    row_html = row_html.replace(
                        "<Количество>", str(getattr(service, "quantity_was_used", "0"))
                    )
                    row_html = row_html.replace(
                        "<Гарантия>", str(getattr(service, "days_of_garanty", "0"))
                    )
                    row_html = row_html.replace(
                        "<СтоимостьУслуги>", str(getattr(service, "service_price", "0"))
                    )
                    summary_price += getattr(service, "service_price", 0)
                    row_html = row_html.replace("<СуммаУслуг>", str(summary_price))
                    generated_rows += row_html

                # Здесь я заменяю строку с переменными на отформатированную
                template_html = template_html.replace(
                    single_row_template, generated_rows
                )

            else:
                generated_rows = '<tr><td colspan="7" style="text-align: center; padding: 8px; color: #718096; font-style: italic;">Услуги не оказывались</td></tr>'
                # Здесь я заменяю строку с переменными на отформатированную
                template_html = template_html.replace(
                    single_row_template, generated_rows
                )

        # ЗАТЕМ ИДЕТ ЗАМЕНА ТЕХ ОБЬЕКТОВ, КОТОРЫЕ НЕ НАХОДЯТСЯ ВНУТРИ ТАБЛИЦЫ
        # Для переменной и ее значения из списка элементов словаря:
        for tag, get_value_func in DOCUMENT_VARIABLES.items():
            # Если триггер-переменная в самом шаблоне документа:
            if tag in template_html:
                try:
                    # Вызов лямбда-функции с передачей данных и отдачей от нее самого результата
                    replacement_value = get_value_func(
                        order,
                        services,
                        company_inf,
                        reason_for_refusal=reason_for_refusal,
                    )
                    # Вставка полученного результата от replacement_value
                    template_html = template_html.replace(tag, str(replacement_value))
                except Exception as e:
                    print(f"Произошла ошибка: ключ: {tag}, {get_value_func}, {e}")
                    # Если у какого-то поля нет данных, просто заменяем на пустую строку, чтобы тег не мозолил глаза
                    template_html = template_html.replace(tag, "")

        return template_html

    # Предлагает список документов на печать
    def get(self, request, *args, **kwargs):

        connected_id = request.GET.get("get_id_order")
        context = {"connected_id": connected_id}
        print(connected_id)
        return render(
            request,
            "orders/print_document/print_document.html",
            context,
        )

    # Принимает один из выбранных документов и печатает его
    def post(self, request, *args, **kwargs):

        connected_id = request.POST.get("get_id_order")
        reason_for_refusal = request.POST.get("reason_for_refusal")
        get_name_document = request.POST.get("name_document")
        print(connected_id)
        print(get_name_document)
        try:

            # Получаю сначала "Шаблон выбранного документа":
            document_html = DocumentInformation.objects.get(
                user=request.user, name=get_name_document
            )

            # Получаю данные по заказу:
            get_order = Orders.objects.get(user=request.user, id=connected_id)

            # Получаю все работы, привязанные к нашему заказу:
            services = CreateServiceWork.objects.filter(
                user=request.user, connected_id=get_order.id
            )

            # Получаю данные о сервисном центре:
            company_inf = ServiceInfo.objects.get(user=request.user)

            rendered_document = PrintSelectedDocument.replace_fields_for_document(
                document_html.content,
                get_order,
                services,
                company_inf,
                reason_for_refusal,
            )

            context = {"order": get_order, "rendered_document": rendered_document}

            # Отдается шаблон самой печати акта о выполненных работах
            response = render(
                request, "orders/tinymce_documents/print_success_work.html", context
            )

            return response

        except Exception as e:

            msg = f"Ошибка: {e}"
            print(msg)
            return HttpResponse(status=400)
