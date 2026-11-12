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
from django.db.models.functions import Cast
from django.shortcuts import render
from django.db.models import Q, Value
from django.db.models.functions import Concat
from orders.models import Orders


# Данный класс отвечает за показ существующих данных клиента (если они есть в БД)
@method_decorator([login_required, never_cache], name="dispatch")
class DiscountCalculation(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        try:

            # Получаю значение (число, рубли / число, проценты)
            get_selected_parameter = request.POST.get("discount_value")

            # Узнаю айди заказа (чтобы можно было соединить логику подсчета ремонта в рублях)
            get_order = Orders.objects.select_for_update().get(
                user=request.user, id=request.POST.get("connected_id")
            )

            if get_selected_parameter == "rub":
                get_order.discount = 

        except Exception as e:
            ...
