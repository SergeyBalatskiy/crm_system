from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from django.shortcuts import render
from django.db.models import Q, TextField, F
from django.views import View
from django.db.models.functions import Cast

# Данный класс отвечает за обычный показ склада
@method_decorator(login_required(), name='dispatch') 
class StorageCustomView(View):

    def get(self, request, *args, **kwargs):

        # Получаю объект из БД для показа уже созданных когда-либо товаров/актуальных
        qs = StorageInfo.objects.filter(user=request.user).order_by('-created_at')

        # Если у нас НЕ пришел запрос пришел через AJAX (или HTMX) — отдаем все
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            context = {'storage_actual_items': qs}
            return render(request, 'storage/main-storage.html', context)

        # В противном случае:
        # Для удобного будущего суммарного поиска через Q (или)
        main_q = Q()

        # "Переформатирую данные" из инта в текст
        qs = qs.annotate(
            buy_price_str=Cast('buy_price', output_field=TextField()),
            individual_code_str=Cast('individual_code', output_field=TextField()),
            retail_price_str=Cast('retail_price', output_field=TextField()),
            quantity_at_the_purchase_str=Cast('quantity_at_the_purchase', output_field=TextField()),
            minimum_items_for_notification_str=Cast('minimum_items_for_notification', output_field=TextField()),
            remainder_str=Cast('remainder', output_field=TextField())
                )

        # Поиск по количеству оставшегося товара
        min_items_remainder = request.GET.get('min_items_remainder')
        # Если тумблер переведен в ДА:
        if min_items_remainder == 'yes':
            # Мгновенно не доставая каждый обьект, фильтрую каждый "слот" на меньшее количество
            main_q &=Q(remainder__lte=F('minimum_items_for_notification'))

        # Поиск по "Быстрому поиску"
        fast_search = request.GET.get('fast_search_all', '').strip()
        if fast_search:

            # "Переназначенные 6 переменных с уже строковым типом я закидываю в фильтр"
            # value.strip() - обязательно, ведь именно это и является тем, ЧТО ввел пользователь! (предварительно
            # форматирую еще)
            text_q = (
                Q(name_product__icontains=fast_search) | 
                Q(individual_code_str__icontains=fast_search) | 
                Q(buy_price_str__icontains=fast_search) | 
                Q(supplier__icontains=fast_search)|
                Q(retail_price_str__icontains=fast_search) | 
                Q(quantity_at_the_purchase_str__icontains=fast_search) | 
                Q(minimum_items_for_notification_str__icontains=fast_search) | 
                Q(remainder_str__icontains=fast_search))

            # Привязываю к глобальному поиску
            main_q &=text_q

        # Поиск по дате (состоит из СТАРТ и ФИНИШ)
        date_start_input = request.GET.get('date_start_input')
        date_end_input = request.GET.get('date_end_input')
        # Если выбраны даты СТАРТ и ФИНИШ:
        if date_start_input and date_end_input:
            # Получаю результат от СТАРТ до ФИНИШ
            main_q &= Q(created_at__range=(date_start_input, date_end_input))

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        qs = qs.filter(main_q)

        context = {'storage_actual_items' : qs}
        return render(request, 'storage/partials/main-list.html', context)


        
        