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
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models.functions import Cast
from django.shortcuts import render, redirect
from django.db.models import Q, Value
from django.db.models.functions import Concat
from orders.models import Orders, CreateServiceWork


# Данный класс отвечает за показ существующих данных клиента (если они есть в БД)
@method_decorator([login_required, never_cache], name="dispatch")
class CountDsc(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):

        try:

            getted_value = request.GET.get("discount_value")

            # Получаю значение (число, рубли / число, проценты)
            get_insert_count = int(float(getted_value)) if getted_value != "" else 0

            if get_insert_count < 0:
                get_insert_count = 0

            connected_id = request.GET.get("get_id_order")

            # Узнаю айди заказа (чтобы можно было соединить логику подсчета ремонта в рублях)
            get_order = Orders.objects.select_for_update().get(
                user=request.user, id=connected_id
            )

            # Получаю QerySet всех работ (ради суммы)
            get_sum_repair = CreateServiceWork.objects.filter(
                user=request.user, connected_id=connected_id
            ).aggregate(total_sum=Sum("service_price"))
            total_price = get_sum_repair["total_sum"] or 0

            # Если значение "тумблера" - рубли
            if request.GET.get("discount_type") == "rub":
                get_order.discount = get_insert_count
            else:
                get_order.discount = (total_price * get_insert_count) // 100

            # Защита от дураков)))
            if get_order.discount > total_price:
                get_order.discount = total_price

            get_order.save()

            response_data = {
                "discount": get_order.discount,
                "total": total_price - get_order.discount,
            }

            response = JsonResponse(response_data)
            response["HX-Trigger"] = "refreshOrders"
            return response

        except Orders.DoesNotExist:
            return HttpResponse("Заказ не найден", status=404)

        except Exception as e:
            # Логируем ошибку для себя в консоль, а клиенту отдаем понятный ответ
            print(f"Ошибка при расчете скидки: {total_price - get_order.discount}")
            return HttpResponse("Ошибка при пересчете скидки", status=400)
