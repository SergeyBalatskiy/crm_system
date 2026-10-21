from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Orders
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
from django.utils import timezone
from django.db.models.functions import Concat

# Данный класс отвечает за показ конкретной информации о клиенте (о заказе)
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowClientOrder(View):

    # Отвечает за показ уже созданной заявки о клиенте
    def get(self, request, *args, **kwargs):
        get_id_order = request.GET.get('get_id_order')
        get_order = Orders.objects.filter(user = request.user, id=get_id_order).first()
        context = {"get_order":get_order}
        print(get_order)
        return render(request, 'orders/show_getted_order/show_getted_form.html', context)
        
    # Отвечает за принятие каких-либо изменений(и их сохранение) в заявке
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        ...