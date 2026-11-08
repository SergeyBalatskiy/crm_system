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
from profile_user.models import StatusCategory
from orders.models import Orders

# Данный класс отвечает за показ и изменение категории статуса заказа
@method_decorator([login_required, never_cache], name='dispatch') 
class ChangeStatusOrder(View):

    # Отдаю все активные категории, которые есть в БД
    def get(self, request, *args, **kwargs):

        # Получаю айдишник нашего заказа
        get_id_order = request.GET.get('get_id_order')

        # Получаю все существующие категории
        get_all_categories = StatusCategory.objects.filter(user=request.user)
        context = {'get_id_order' : get_id_order}
        
        # Добавляю дополнительный фильтр, получая все успешные категории + запись в контекст
        context['success'] = get_all_categories.filter(category='success')
        context['in_process'] = get_all_categories.filter(category='in_process')
        context['finished'] = get_all_categories.filter(category='finished')
        context['deferred'] = get_all_categories.filter(category='deferred')

        return render(request, 'orders/partials/change_current_category.html', context)

    # Получает айдишник конкретной актуальной категории, и, делает ее актуальной
    def post(self, request, *args, **kwargs):
        try:
            # Получаю айдишник категории
            get_id_category = request.POST.get('actual_id')

            print(get_id_category)

            # Получаю айдишник заказа
            get_id_order = request.POST.get('get_id_order')

            print(get_id_order)

            # Получаю категорию из БД
            get_selected_category = StatusCategory.objects.get(user=request.user, id=get_id_category)

            # Беру сам заказ, чтобы в нем обновить статус
            update_category = Orders.objects.select_for_update().get(user=request.user, id=get_id_order)

            # Обновляю в заказе цвет, название и eng_name категории
            update_category.name_category = get_selected_category.name
            update_category.color_category = get_selected_category.color
            update_category.category_eng = get_selected_category.category
            update_category.save()

            return HttpResponse(status=204)

        # Хочу тут как то выводить если случится какая то ошибка...
        except Exception as e:
            msg = f'Ошибка: {e}'
            print(msg)
            return HttpResponse(msg, status=400)