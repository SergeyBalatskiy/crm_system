from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from finance.models import CashAccount, FinanceHistoryInfo
from django.shortcuts import render
from django.db.models import Q, TextField, F
from django.views import View
from django.db.models.functions import Cast
from datetime import timedelta
from datetime import datetime
from django.utils import timezone

# Данный класс отвечает за обычный показ баланса сервисного центра + фильтр + истории
@method_decorator(login_required(), name='dispatch') 
class MainCashAndHistoryView(View):

    def get(self, request, *args, **kwargs):

        # Получаю / создаю баланс кассы
        get_main_balance, created = CashAccount.objects.get_or_create(user=request.user)
        # Беру все данные пользователя
        qs = FinanceHistoryInfo.objects.filter(user=request.user).order_by('-created_at')

        # Если у нас НЕ пришел запрос через AJAX (или HTMX) — отдаем ТОЛЬКО кусок со списком
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {'history_finance' : qs, 'cash': get_main_balance, }
            return render(request, 'finance/main_balance.html', context)
        
        # В противном случае:
        # Для удобного будущего суммарного поиска через Q (или)
        main_q = Q()

        # "Переформатирую данные" из инта в текст
        qs = qs.annotate(
            number_in_the_operation_str=Cast('number_in_the_operation', output_field=TextField()),
            product_code_str=Cast('product_code', output_field=TextField()),
            )

        # Поиск по типу операции
        operation = request.GET.get('selected_finance_operation')
        if operation:
            operations_dict = {'income':'Поступление',
                                   'outcome':'Исход',}
            op_value = operations_dict.get(operation)
            if op_value:
                main_q &= Q(type_of_operation=op_value)

        # Поиск по категории операции
        category = request.GET.get('selected_finance_category')
        if category:
            category_dict = {'Продажа':'Продажа',
                             'Покупка':'Покупка',
                             'Гарантийный возврат':'Гарантийный возврат',
                             'Прочее':'Прочее'
                            }
            cat_value = category_dict.get(category)
            if cat_value:
                main_q &= Q(category_of_operation=cat_value)

        # Поиск по "Быстрому поиску"
        fast_search = request.GET.get('fast_search_all', '').strip()
        if fast_search:

            # "Переназначенные 2 переменные с уже строковым типом я закидываю в фильтр"
            # value.strip() - обязательно, ведь именно это и является тем, ЧТО ввел пользователь! (предварительно
            # форматирую еще)
            text_q = (
                Q(product_name__icontains=fast_search) | 
                Q(product_code_str__icontains=fast_search) | 
                Q(number_in_the_operation_str__icontains=fast_search) |
                Q(comment__icontains=fast_search))
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
                    main_q &= Q(created_at__range=date_finded)

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

        context = {
            'history_finance': qs,
            'cash': get_main_balance,
        }

        # Если это AJAX-запрос — отдаем только список карточек
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'finance/partials/history-list.html', context)

        return render(request, 'finance/main_balance.html', context)
