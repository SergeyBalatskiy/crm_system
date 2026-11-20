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
class FindWorkersInformation(View):

    def get(self, request, *args, **kwargs):

        # Получаю абсолютно всех клиентов по запросу, которые связаны с этим СЦ
        qs = WorkersInfo.objects.filter(user=request.user)

        if 'master' in request.GET:
            # Поиск по "названию(имя, фамилия, роль)" мастера
            find_master = request.GET.get('master', '').strip()
            if find_master:
                lst_master = find_master.split()
                text_q = Q()
                for part in lst_master:
                    text_q = (Q(name__icontains=part) | 
                            Q(surname__icontains=part) |
                            Q(role__icontains=part))
                # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
                qs = qs.filter(text_q)          

            context = {'workers_info': qs, 'field_key':'master' }
            return render(request, 'orders/partials/worker_dropdown.html', context)

        if 'manager' in request.GET:
            # Поиск по "названию(имя, фамилия, роль)" менеджера
            find_manager = request.GET.get('manager', '').strip()
            if find_manager:
                lst_manager = find_manager.split()
                text_q = Q()
                for part in lst_manager:
                    text_q = (Q(name__icontains=part) | 
                                Q(surname__icontains=part) |
                                Q(role__icontains=part))
                # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
                qs = qs.filter(text_q)
                
            context = {'workers_info': qs, 'field_key': 'manager'}
            return render(request, 'orders/partials/worker_dropdown.html', context)
        
        return HttpResponse('')