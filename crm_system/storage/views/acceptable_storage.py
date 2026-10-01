from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from storage.forms import StorageAcceptableForm
from storage.models import StorageInfo, HistoryStorageInfo
from django.contrib import messages
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from finance.models import CashAccount, FinanceHistoryInfo
from django.db.models import F
from django.urls import reverse
from django.http import HttpResponse
import json
from django.views.decorators.cache import never_cache

# Данный класс отвечает за показ сайта где можно добавить новые поступления на склад
@method_decorator([never_cache, login_required], name='dispatch') 
class StorageAcceptableCustomView(TemplateView):

    template_name = 'storage/acceptance-storage.html'

    @staticmethod
    def htmx_toast_error(message):
        print('Сработала функция ерор')
        """Возвращает 204 No Content"""
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'level': 'error',
                'message': message
            }
        })
        return response

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Получаю все формсеты, которые есть
        formset = StorageAcceptableForm(request.POST)
        # ОБЯЗАТЕЛЬНО НУЖНО ЧТОБЫ ПРИХОДИЛ ФОРМСЕТ ТАКЖЕ И С КОММЕНТАРИЕМ И ЧТОБЫ ОН БЫЛ ПРИВЯЗАН К АЙДИШНИКУ И САМОМУ ТОВАРУ

        # Валидация форм (пропуск не важных полей) + сохранение важных
        if not formset.is_valid():
            return(self.htmx_toast_error('Пожалуйста, заполните до конца пустые поля!'))

        try:
            # Остановка сохранения 
            instances = formset.save(commit=False)
            now = timezone.now()
            global_sum = 0
            list_for_add_finance_history = []
            list_for_add_history_storage = []
                
            if not instances:   
                return(self.htmx_toast_error('Пожалуйста, заполните форму на добавление!'))

            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю <- StorageInfo
            for instance in instances:
                instance.user = request.user
                instance.remainder = instance.quantity_at_the_purchase
                instance.save()

                # Придаю "Коду товара" такой же id как и у истинного айдишника 
                instance.individual_code = instance.id

                # Беру цену этого товара и записываю ее в переменную current_price_summary
                current_price_summary = instance.quantity_at_the_purchase * instance.buy_price
                # Добавляю суммарно глобальную переменную, показывающую цену всех товаров совместно
                global_sum += current_price_summary

                # Список list_for_add_finance_history позволяет внедрить команды с добавлением обьектов в 1 переменную, и затем в конце
                # создать это множество обьектов!
                list_for_add_finance_history.append(HistoryStorageInfo(user=request.user, type_of_operation_history = 'Поступление', 
                individual_code_history = instance.individual_code, name_product_history = instance.name_product,
                quantity_history = instance.quantity_at_the_purchase, buy_price_history = instance.buy_price,
                supplier_history = instance.supplier, remainder_history = instance.remainder,
                time_of_operation_history = now))

                # Список list_for_add_history_storage позволяет внедрить команды с добавлением обьектов в 1 переменную, и затем в конце
                # создать это множество обьектов!
                list_for_add_history_storage.append(FinanceHistoryInfo(user=request.user, 
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.OUTCOME, category_of_operation = FinanceHistoryInfo.CategoryOfOperation.BUY,
                number_in_the_operation = instance.buy_price * instance.quantity_at_the_purchase, product_name = instance.name_product,
                product_code = instance.individual_code, supplier = instance.supplier,
                comment = f'Покупка товара: {instance.name_product}, в кол-ве: {instance.quantity_at_the_purchase}, за {instance.buy_price * instance.quantity_at_the_purchase} ₽.')
                )

            # Если цикл добавления товаров произошел успешно, осталось только "закомитить" два списка, вычесть с кассы актуальную цену закупки,
            # и отдать готовый результат!
            # BULK_CREATE!!!
            HistoryStorageInfo.objects.bulk_create(list_for_add_finance_history)
            FinanceHistoryInfo.objects.bulk_create(list_for_add_history_storage)

            # На уровне F выражения меняю баланс в отрицательную сторону из-за покупки
            CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') - global_sum)
                                        
        except Exception as e:
            return(self.htmx_toast_error(f'Ошибка:{e}'))

        messages.success(request, 'Поступление товара(-ров) прошло успешно!')
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = reverse('filter_and_history_storage')
            return response

        return redirect('filter_and_history_storage')
        
    def get(self, request, *args, **kwargs):
        # Получаю форму для добавления товара
        formset = StorageAcceptableForm(queryset=StorageInfo.objects.none())
        return render(request, self.template_name, {'form_acceptable' : formset})
