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
from profile_user.models import WorkersInfo
from django.db.models import Q, Value
from django.db.models.functions import Concat

# Данный класс отвечает за показ существующих "рабочих" (Обращение в воркерс и показ)
@method_decorator([login_required, never_cache], name='dispatch') 
class ServiceWorkCreate(View):

    def get(self, request, *args, **kwargs):

        # Тут показывается (предположительно) формсет с формой на создание услуг
        return render(request, 'service_work.html')

    def post(self, request, *args, **kwargs):

        # Получаю обьект с названием работы 



            user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='create_service_work')
    
    # Данное поле отвечает за соединение с УНИКАЛЬНЫМ КЛЮЧОМ определенного заказа
    connected_id = models.ForeignKey(Orders, on_delete=models.CASCADE)

    # Оказанная услуга: (ее название)
    service_provided = models.CharField(max_length=300)

    # Дата оказанной услуги:
    service_was_created = models.DateTimeField(default=timezone.now)

    # Цена оказанной услуги
    service_price = models.DecimalField(decimal_places=0, max_digits=11)

    # ------------------------------------------------------------------
    # Здесь идет запоминание важной информации о товаре в случае отката (удаления работы)
    # ------------------------------------------------------------------

    # Количество используемого товара в ремонте
    quantity_was_used = models.IntegerField()

    # Цена товара в закупке
    detail_buy_price = models.DecimalField(decimal_places=0, max_digits=11, null=True, blank=True)

    # Цена товара в продажу
    detail_retail_price = models.DecimalField(decimal_places=0, max_digits=11, null=True, blank=True)

    # Минимальное количество товара для запоминания
    detail_minimum_items_for_not = models.IntegerField(default=5)

    # Поставщик 
    detail_supplier = models.CharField(max_length=120, blank=True, null=True)

    # Индивидуальный код, который запоминается для определенной детали (если она еще есть в БД)
    detail_id = models.IntegerField()

    # Количество на момент закупки
    detail_quantity_was_buyed = models.IntegerField()

    # ------------------------------------------------------------------