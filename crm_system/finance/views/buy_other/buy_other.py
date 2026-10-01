from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo, StorageInfo
from django.shortcuts import render, redirect
from finance.forms import SellCustomForm
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from django.views.decorators.cache import never_cache
from finance.models import CashAccount, FinanceHistoryInfo
from django.db.models import F
import json

# Данный класс отвечает за показ сайта, внести средства (Прочее, поступление)
@method_decorator([never_cache, login_required], name='dispatch') 
class BuyFinanceCustomView(TemplateView):

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

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Получаю все формсеты, которые есть
        formset = SellCustomForm(request.POST)

        # Если не заполнены корректно:
        if not formset.is_valid():
            return self.htmx_toast_error("Пожалуйста, проверьте поля на корректность ввода и повторите попытку.")
                        
        # Остановка сохранения 
        instances = formset.save(commit=False)
        # Обработка еще одного некорректного случая:
        if not instances:
            return self.htmx_toast_error('Пожалуйста, проверьте поля на корректность ввода и повторите попытку!')
            
        # Список на добавление истории поступления средств 
        list_to_add_finane_history = []
        
        # "Глобальная" переменная, отвечающая за возврат денежных средств всех товаров
        global_sum = 0
        
        try:
      
            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            for instance in instances:
                
                # Добавляю в переменную суммарный баланс
                global_sum += instance.number_in_the_operation

                # Проверяю, какой комментарий у меня был записан:
                if not instance.comment:
                    instance.comment = "Исход финансов (Прочее)"

                # Проверяю "поставщика" на поступление финансов:
                if not instance.supplier:
                    instance.supplier = "Прочее"
                    
                # Сделал историю операции:
                # Список list_for_add_history_storage позволяет внедрить команды с добавлением обьектов в 1 переменную, и затем в конце
                # создать это множество обьектов!
                list_to_add_finane_history.append(FinanceHistoryInfo(user=request.user, 
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.OUTCOME, category_of_operation = FinanceHistoryInfo.CategoryOfOperation.OTHER,
                number_in_the_operation = instance.number_in_the_operation, product_name = instance.product_name,
                supplier = instance.supplier, comment = instance.comment))          

            # Если цикл поступления произошел успешно, осталось только "закомитить", добавить в кассу 
            # BULK_CREATE!!!
            FinanceHistoryInfo.objects.bulk_create(list_to_add_finane_history)
            # На уровне F выражения меняю баланс в положительную сторону из-за возврата
            CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') - global_sum)

            if request.headers.get('HX-Request'):
                msg = 'Поступление средств прошло успешно.'
                print(msg)
                messages.success(request, msg)
                response = HttpResponse()
                response['HX-Redirect'] = reverse('filter_and_history_storage')
                return response
                                                    
        except Exception as e:
            # Статус 204 если произошла ошибка
            return self.htmx_toast_error(f'Ошибка: {e}.')
                                                    
                
