from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from django.shortcuts import render
from storage.models import HistoryStorageInfo
from django.db.models import Q
from datetime import timedelta
from django.views import View
from django.utils import timezone

# Данный класс отвечает за показ определенных данных исходя из фильров и показ всех данных из истории
@method_decorator(login_required(), name='dispatch') 
class FilterHistoryCustomView(View):
    def get(self, request, *args, **kwargs): 

        # Беру все данные пользователя
        qs = HistoryStorageInfo.objects.filter(user=request.user).order_by('-time_of_operation_history')

        # Если у нас НЕ пришел запрос пришел через AJAX (или HTMX) — отдаем ТОЛЬКО кусок со списком
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {'storage_history_items' : qs}
            return render(request, 'storage/history-storage.html', context)

        # В противном случае:

        # Для удобного будущего суммарного поиска через Q (или)
        main_q = Q()

        # "Переформатирую данные" из инта в текст
        qs = qs.annotate(
            buy_price_str=Cast('buy_price_history', output_field=TextField()),
            individual_code_str=Cast('individual_code_history', output_field=TextField())
                )

        # Поиск по типу операции
        operation = request.GET.get('search_history_operation')
        if operation:
            operations_dict = {'acceptable_data':'Поступление',
                                   'removal_data':'Возврат без возмещения денежных средств',
                                   'garanty_removal_data':'Гарантийный возврат'}
            op_value = operations_dict.get(operation)
            if op_value:
                main_q &= Q(type_of_operation_history=op_value)

        # Поиск по "Быстрому поиску"
        fast_search = request.GET.get('fast_search_all', '').strip()
        if fast_search:

            # "Переназначенные 2 переменные с уже строковым типом я закидываю в фильтр"
            # value.strip() - обязательно, ведь именно это и является тем, ЧТО ввел пользователь! (предварительно
            # форматирую еще)
            text_q = (
                Q(name_product_history__icontains=fast_search) | 
                Q(individual_code_str__icontains=fast_search) | 
                Q(buy_price_str__icontains=fast_search) | 
                Q(supplier_history__icontains=fast_search))
                # Привязываю к глобальному поиску
            main_q &=text_q

        # Поиск по дате
        date_selected = request.GET.get('search_date_operation')
        if date_selected:

                # Получение точного момента времени
                now = timezone.now()
                # Получение только даты (без времени)
                today = now.date()

                # Словарь с датами в зависимости от выбранного дня
                dates_dict = {'date_today' : (today, now), 
                              'date_yesterday' : (today - timedelta(days=1), today),
                              'date_this_week' : (today - timedelta(days=7), now),
                              'date_this_month' : (today - timedelta(days=30), now)
                              }
                date_finded = dates_dict.get(date_selected)
                if date_finded:
                    main_q &= Q(time_of_operation_history__range=date_finded)

        # Поиск по дате (состоит из СТАРТ и ФИНИШ)
        date_start_input = request.GET.get('date_start_input')
        date_end_input = request.GET.get('date_end_input')
            # Если выбраны даты СТАРТ и ФИНИШ:
        if date_start_input and date_end_input:
            # Получаю результат от СТАРТ до ФИНИШ
            main_q &= Q(time_of_operation_history__range=(date_start_input, date_end_input))
        
        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        qs = qs.filter(main_q)

        context = {'storage_history_items' : qs}
        return render(request, 'storage/partials/history-list.html', context)


        
        