from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from finance.models import CashAccount, FinanceHistoryInfo
from django.shortcuts import render, redirect
from django.db.models import F
from django.views import View
from finance.forms import InsertCashForm, CommentCashForm
from storage.models import HistoryStorageInfo, StorageInfo
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from finance.models import FinanceHistoryInfo, CashAccount
from itertools import zip_longest
import json


# Данный класс отвечает за обычный показ баланса сервисного центра
@method_decorator(login_required(), name='dispatch') 
class InsertCashInBalance(View):

    @staticmethod
    def htmx_toast_error(message):
        """Возвращает 204 No Content"""
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'level': 'error',
                'message': message
            }
        })
        return response

    # Отправка данных на POST для создания истории в storage + финансовой операции в finance
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        formset = InsertCashForm(request.POST)
        formset_comment = CommentCashForm(request.POST)

        if formset.is_valid():
                
            # Остановка сохранения 
            instances = formset.save(commit=False)
            comments = formset_comment.save(commit=False)

            if not instances:
                return self.htmx_toast_error('Пожалуйста, выберите хотя бы один товар на продажу!')

            # Счетчик для суммарного подсчета прибыли
            summary_cash = 0

            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            #    товар    коммент                  товары    комменты
            for instance, comment in zip_longest(instances, comments, fillvalue=None):
                try:
                    history_data = StorageInfo.objects.filter(individual_code=instance.individual_code_history).first()
                    instance.user = request.user

                    if history_data is None:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        return self.htmx_toast_error(f'Ошибка: вы попытались повторно продать товар с кодом {instance.name_product_history}, количество которого на момент прошлой продажи уже стало 0.')

                    instance.name_product_history = history_data.name_product
                    instance.type_of_operation_history = "Продажа товара"
                    instance.individual_code_history = history_data.individual_code
                    current_remainder_instance = instance.quantity_history

                    # Проверяю на "верность" введенного количества товара:
                    if history_data.remainder - current_remainder_instance < 0:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        return self.htmx_toast_error(f'Ошибка: товара {history_data.name_product} на складе меньше, чем вы указали под продажу!')

                    instance.remainder_history = history_data.remainder - current_remainder_instance
                    history_data.remainder = history_data.remainder - current_remainder_instance
                    instance.time_created_history = history_data.created_at
                    instance.time_of_operation_history = timezone.now()
                    instance.save()

                    # Счетчик который суммарно показывает заработок:
                    summary_cash += (instance.buy_price_history * instance.quantity_history)
                    
                    # Если комментарий не задан:
                    if not comment:
                        comment = f'Продажа товара: {instance.name_product_history}, в кол-ве: {instance.quantity_history}, на сумму: {instance.buy_price_history * instance.quantity_history} ₽.'

                    # Добавляю новую историю операции продажи
                    FinanceHistoryInfo.objects.create(user=request.user, 
                    type_of_operation = FinanceHistoryInfo.TypeOfOperation.INCOME,
                    category_of_operation = FinanceHistoryInfo.CategoryOfOperation.SALE,
                    product_name = instance.name_product_history, product_code = instance.individual_code_history,
                    number_in_the_operation = instance.buy_price_history * instance.quantity_history,
                    comment = comment)
                    
                    # Внесение денег в кассу:
                    # На уровне F выражения меняю баланс в положительную сторону (так как продажа)
                    CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') + (instance.buy_price_history * instance.quantity_history))

                    # Обновляю обьект в БД (если его количество 0, то он не нужен, удаляем!)
                    history_data.save()
                    if history_data.remainder == 0:
                        history_data.delete()

                except TypeError:
                    transaction.set_rollback(True)
                    return self.htmx_toast_error(f'Необходимо указать цену для продажив!')  

                except Exception as e:
                    # Статус 204 если произошла ошибка + транзакция
                    transaction.set_rollback(True)
                    return self.htmx_toast_error(f'Ошибка: {e}')   
                
            if request.headers.get('HX-Request'):
                msg = f'Продажа прошла успешно! Заработано: {summary_cash}'
                messages.success(request, msg)
                response = HttpResponse()
                response['HX-Redirect'] = reverse('main_cash')
                return response

         # Статус 204 если ошибка
        return self.htmx_toast_error('Пожалуйста, проверьте поля на корректность ввода и повторите попытку.')   

    def get(self, request, *args, **kwargs):
        # Получаю форму для продажи товара, историю записываю сюда, а финансовую операцию запишу отдельно
        formset = InsertCashForm(queryset=HistoryStorageInfo.objects.none())
        return render(request, 'finance/sell/sell-item.html', {'sell_form' : formset})