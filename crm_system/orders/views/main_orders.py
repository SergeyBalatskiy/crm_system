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
from django.db.models import Q

# Данный класс отвечает за показ всех созданных заявок на ремонт (orders) + фильтр через уже знакомый метод
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowAndFilterOrders(View):

    # Надо еще подумать над тем, нужна ли она вообще здесь...
    @staticmethod
    def htmx_toast_error(message):
        print('Сработала функция ерор')
        print(message)
        """Возвращает 204 No Content"""
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'level': 'error',
                'message': message
            }
        })
        return response
    
    def get(self, request, *args, **kwargs):

        # Получаю абсолютно все заявки на ремонт (Действующие / Готовые / Выданные / Отложенные)
        # Фильтрую по самому свежему заказу!
        qs = Orders.objects.filter(user=request.user).order_by('-created_at')

        # Если у нас НЕ пришел запрос через AJAX (или HTMX) — отдаем ТОЛЬКО кусок со списком
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {'orders' : qs}
            return render(request, 'orders/orders.html', context)
        
        # В противном случае:
        # Для удобного будущего суммарного поиска через Q (или)
        main_q = Q()

        # "Переформатирую данные" из инта в текст
        qs = qs.annotate(
            # Тут пока что два поля которые находятся в БД (Orders): id (уникальный код заявки), price (цена)
            id_str=Cast('id', output_field=TextField()),
            price_str=Cast('price', output_field=TextField()),
            )

        # Поиск по типу операции
        status = request.GET.get('selected_order_status')
        if status:

            # {"name": "На ремонте", "color": "#ac03f4", "category":"in_process"},
            # {"name": "На согласовании", "color": "#ff8c00", "category":"deferred"},
            # {"name": "Готов", "color": "#2ecc71", "category":"success"},
            # {"name": "Отказ", "color": "#e74c3c", "category":"finished"},

            """Суть заключается в том, что выбранный нами статус уже и будет нести в себе нужный для нас фильтр в БД"""
            # С POST-запроса может прийти следующий статус (от status = request.GET.get('selected_order_status')):  
            # in_process, deferred, success, finished
            main_q &= Q(status=status)

            # ПРОДОЛЖИТЬ ДАЛЬШЕ ЗДЕСЬ!!!

        # Поиск по "Быстрому поиску"
        fast_search = request.GET.get('fast_search_all', '').strip()
        if fast_search:

            # Тут у меня в будущем будет фильтр по определенным полям...
            text_q = (
                Q(...__icontains=fast_search) | 
                Q(...__icontains=fast_search) | 
                Q(...__icontains=fast_search) |
                Q(...__icontains=fast_search) |
                Q(...__icontains=fast_search) | 
                Q(...__icontains=fast_search) |)
                # Привязываю к глобальному поиску
            main_q &=text_q

        # Поиск по дате (состоит из СТАРТ и ФИНИШ)
        date_start_input = request.GET.get('date_start_input')
        date_end_input = request.GET.get('date_end_input')
            # Если выбраны даты СТАРТ и ФИНИШ:
        if date_start_input and date_end_input:
            # Получаю результат от СТАРТ до ФИНИШ
            date_end_input = datetime.strptime(date_end_input, "%Y-%m-%d").date()
            main_q &= Q(created_at__range=(date_start_input, date_end_input+timedelta(days=1)))
        
        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        qs = qs.filter(main_q)

        context = {'orders': qs}

        return render(request, 'orders/orders.html', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Данная функция отвечает за создание заявки на ремонт
        ...
