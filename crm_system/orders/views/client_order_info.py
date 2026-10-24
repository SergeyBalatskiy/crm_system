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
from profile_user.models import FormsForOrder

# Данный класс отвечает за показ конкретной информации о клиенте (о заказе)
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowClientOrder(View):

    # Отвечает за показ уже созданной заявки о клиенте
    def get(self, request, *args, **kwargs):
        get_id_order = request.GET.get('get_id_order')
        get_order = Orders.objects.filter(user = request.user, id=get_id_order).first()

        # Получаю действующую форму из Базы данных
        get_original_form = FormsForOrder.objects.filter(user=request.user).first()
        sections = get_original_form.json_forms.get('sections', [])

        # Получаю уже введенные данные из созданной заявки в базе данных
        saved_data = get_order.form_with_order_information.get('order_dict')
        # "Упаковываю" каждые из элементов в словарь(чтобы можно было потом просто достать)
        saved_map = {block['id']: block for block in saved_data}

        # Прохожусь индивидуально по каждому обьекту из формы из базы данных (актуальной)
        for section in sections:
            # После того как взял обьект - мне нужно у этого обьекта запомнить айди его 
            sec_id = section.get('id')
            # Получаю именно обьект с уже введенными данными благодаря айдишнику из БД!
            sec_saved_values = saved_map.get(sec_id, [])
            # Здесь проходит логика записывания введенных данных из полученных форм в ключ (данные записываются в как бы основной
            # JSON (главный, который имеет предварительно пустое поле, и это поле в дальнейшем заполняется!)
            for field in section.get('fields'):
                f_key = field.get('field_key')
                field['value'] = sec_saved_values.get(f_key)

        print(sections)

        context = {
            'get_order' : get_order,
            'sections' : sections,
            'current_type' : get_order.type_of_order
        }
        return render(request, 'orders/show_getted_order/show_getted_form.html', context)

    # Отвечает за принятие каких-либо изменений(и их сохранение) в заявке
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        ...