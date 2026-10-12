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

# Данный класс отвечает за показ существующих данных клиента (если они есть в БД)
@method_decorator([login_required, never_cache], name='dispatch') 
class FindClientInformation(View):

    def get(self, request, *args, **kwargs):

        # Получаю абсолютно всех клиентов по запросу, которые связаны с этим СЦ
        qs = Client.objects.filter(user=request.user)

        # Для удобного будущего суммарного поиска через Q (или)
        main_q = Q()

        # Поиск по "названию" клиента
        name_client = request.GET.get('name', '').strip()
        if name_client:
            main_q &= Q(name__icontains=name_client)

        # Поиск по телефону
        phone_client = request.GET.get('phone', '').strip()
        if phone_client:
            main_q &=Q(phone__icontains=phone_client)

        if not name_client and not phone_client:
            qs=qs
        else:
            # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
            qs = qs.filter(main_q)

        context = {'client_info': qs}
        return render(request, 'orders/partials/client_dropdown.html', context)
