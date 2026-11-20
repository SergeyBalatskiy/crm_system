from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from orders.models import Orders
from finance.models import CashAccount, FinanceHistoryInfo
from django.shortcuts import render
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models import Q


# Функция, которая отвечает за фильтрацию "Финансовых данных" и дальнейшее отображение в HTML (В виде диаграммы)
def show_graphical_diagram(request):

    # Беру все данные пользователя
    qs = FinanceHistoryInfo.objects.filter(user=request.user)

    # Все остальное для функции
    type_of_operation = request.GET.get("type_of_operation")
    category_of_operation = request.GET.get("category_of_operation")
    start_day = request.GET.get("start_day")
    finish_day = request.GET.get("finish_day")
    print(type_of_operation)
    print(category_of_operation)

    # Определяю стартовый день
    if (
        start_day
    ):  # gte = означает, что вы берем все, что "выше", чем наш выбранный день
        qs = qs.filter(created_at__date__gte=start_day)
    if (
        finish_day
    ):  # lte = означает, что вы берем все, что "ниже", чем наш  второй выбранный день
        qs = qs.filter(created_at__date__lte=finish_day)
    if type_of_operation:
        qs = qs.filter(type_of_operation=type_of_operation)
    if category_of_operation:
        qs = qs.filter(category_of_operation=category_of_operation)

    # Группировка всех обьектов, полученных в результате фильтрации
    filtered_objects = (
        qs.values("created_at")
        .annotate(
            total_income=Sum(
                "number_in_the_operation", filter=Q(type_of_operation="Поступление")
            ),
            total_outcome=Sum(
                "number_in_the_operation", filter=Q(type_of_operation="Исход")
            ),
        )
        .order_by("created_at")
    )

    # Тут я по порядку получаю ТОЛЬКО ДЕНЬ
    date_time = []

    # Получаю положительные суммы
    income_data = []

    # Получаю отрицательные суммы
    outcome_data = []

    for item in filtered_objects:
        date_time.append(item["created_at"].strftime("%d.%m.%y, %H:%M"))
        income_data.append(int(item["total_income"] or 0))
        outcome_data.append(int(item["total_outcome"] or 0))

    return JsonResponse(
        {
            "date_time": date_time,
            "income_data": income_data,
            "outcome_data": outcome_data,
        }
    )


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
        get_balance, created = CashAccount.objects.get_or_create(
            user=request.user, defaults={"user": request.user, "money_balance": 0}
        )

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

        return render(request, self.template_name, context)
