from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth.models import User
from orders.models import Orders
from finance.models import CashAccount, FinanceHistoryInfo
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, TextField, F
from django.db.models.functions import TruncMonth


# Функция, которая отвечает за фильтрацию "Финансовых данных" и дальнейшее отображение в HTML (В виде диаграммы)
def show_graphical_diagram(
    request,
    header,
    type_of_operation,
    category_of_operation,
    fast_day_seleted,
    start_day,
    finish_day,
):

    # Получаю / создаю баланс кассы
    get_main_balance, created = CashAccount.objects.get_or_create(user=request.user)
    # Беру все данные пользователя
    qs = FinanceHistoryInfo.objects.filter(user=request.user).order_by("-created_at")

    # Если у нас НЕ пришел запрос через AJAX (или HTMX) — отдаем ТОЛЬКО кусок со списком
    if not header == "XMLHttpRequest":
        result_func_context = {
            "history_finance": qs,
            "cash": get_main_balance,
        }
        return result_func_context

    # В противном случае:
    # Для удобного будущего суммарного поиска через Q (или)
    main_q = Q()

    # Поиск по типу операции
    if type_of_operation:
        operations_dict = {
            "income": "Поступление",
            "outcome": "Исход",
        }
        op_value = operations_dict.get(type_of_operation)
        if op_value:
            main_q &= Q(type_of_operation=op_value)

    # Поиск по категории операции
    if category_of_operation:
        category_dict = {
            "Продажа": "Продажа",
            "Покупка": "Покупка",
            "Гарантийный возврат": "Гарантийный возврат",
            "Оказание ремонтных услуг": "Оказание ремонтных услуг",
            "Прочее": "Прочее",
        }
        cat_value = category_dict.get(category_of_operation)
        if cat_value:
            main_q &= Q(category_of_operation=cat_value)

    # "Быстрый" поиск по предложенным из селекта дням:
    if fast_day_seleted:

        # Получение точного момента времени
        now = timezone.now()
        # Получение только даты (без времени)
        today = now.date()

        # Словарь с датами в зависимости от выбранного дня
        dates_dict = {
            "date_today": (today, now),
            "date_yesterday": (today - timedelta(days=1), today),
            "date_this_week": (today - timedelta(days=7), now),
            "date_this_month": (today - timedelta(days=30), now),
        }
        date_finded = dates_dict.get(fast_day_seleted)
        if date_finded:
            main_q &= Q(created_at__range=date_finded)

    # Поиск по дате (состоит из СТАРТ и ФИНИШ)
    # Если выбраны даты СТАРТ и ФИНИШ:
    if start_day and finish_day:
        # Получаю результат от СТАРТ до ФИНИШ
        finish_day = datetime.strptime(finish_day, "%Y-%m-%d").date()
        main_q &= Q(created_at__range=(start_day, finish_day + timedelta(days=1)))

    # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
    qs = qs.filter(main_q)

    result_func_context = {
        "history_finance": qs,
        "cash": get_main_balance,
    }

    return result_func_context


# Отвечает за показ главной информации о клиенте (что-то типо профиля)
@method_decorator(login_required(), name="dispatch")
class UserProfileView(TemplateView):
    template_name = "profile_user/profile.html"

    def get(self, request, *args, **kwargs):

        # Получаю пользователя
        get_user = request.user
        # Получаю заказы
        get_orders = Orders.objects.filter(user=request.user)

        # Вернет самые новые последние заказы (10 штук)
        latest_ten_orders = get_orders.order_by("-created_at")[:10]

        # Получаю весь баланс кассы
        get_balance = CashAccount.objects.get(user=request.user)

        context = {
            "user": get_user,  # Получаю данные "главного пользователя"
            "summary_orders": len(get_orders),  # Подсчитываю количество всех заказов
            "in_progress_orders": get_orders.exclude(
                category_eng__in=[
                    "deferred",
                    "finished",
                ]  # Смотрю количество АКТИВНЫХ заказов БЕЗ статуса завершенный | на обдумывании
            ).count(),
            "balance_cash": get_balance.money_balance,  # Актуальный баланс кассы
            "latest_ten_orders": latest_ten_orders,  # Последние 10 актуальных заказов
        }

        # Заголовок для проверки того, какой запрос мы получили?
        header = request.headers.get(
            "x-requested-with"
        )  # request.headers.get("x-requested-with") в условии

        # Все остальное для функции
        type_of_operation = request.GET.get("type_of_operation")
        category_of_operation = request.GET.get("category_of_operation")
        fast_day_seleted = request.GET.get("fast_day_seleted")
        start_day = request.GET.get("start_day")
        finish_day = request.GET.get("finish_day")

        # Вызываю функцию, которая отвечает за фильтрацию "Финансовых данных" и дальнейшее отображение в HTML (В виде диаграммы)
        result_func_context = show_graphical_diagram(
            request,
            header,
            type_of_operation,
            category_of_operation,
            fast_day_seleted,
            start_day,
            finish_day,
        )

        context.update(result_func_context)

        return render(request, self.template_name, context)
