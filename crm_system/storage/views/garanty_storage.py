from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo, StorageInfo
from django.shortcuts import render, redirect
from storage.forms import GarantyHistoryForm
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from django.views.decorators.cache import never_cache
from finance.models import CashAccount, FinanceHistoryInfo
from django.db.models import F
import json

# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator([never_cache, login_required], name='dispatch') 
class StorageGarantyCustomView(TemplateView):

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
        formset = GarantyHistoryForm(request.POST)

        # Если не заполнены корректно:
        if not formset.is_valid():
            return self.htmx_toast_error("Пожалуйста, проверьте поля на корректность ввода и повторите попытку.")
                        
        # Остановка сохранения 
        instances = formset.save(commit=False)
        # Обработка еще одного некорректного случая:
        if not instances:
            return self.htmx_toast_error('Пожалуйста, выберите хотя бы один товар на списание!')
            
        # Список на добавление истории возврата средств 
        list_to_add_finane_history = []
        
        # Список на добавление истории операции гарантийного возврата
        list_for_add_history_storage = []

        # "Глобальная" переменная, отвечающая за возврат денежных средств всех товаров
        global_garanty_sum = 0

        # Список в котором у меня будут храниться айдишники на удаление тех товаров из StorageInfo, где количество товаров == 0!
        list_to_delete_obj = []

        try:
            # Получаю только айди товаров исходя из формсетов
            codes = [i.individual_code_history for i in instances]
            # Получаю QuerySet`ы и упаковываю их в словарь (1 запрос в БД)
            dict_for_objects = {s.individual_code:s for s in StorageInfo.objects.select_for_update().filter(user=request.user, individual_code__in=codes)}
                        
            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            for instance in instances:
                # Получаю 1 обьект из словаря с StorageInfo - Query`сетами
                selected_object = dict_for_objects.get(instance.individual_code_history)

                # Проверка на наличие введенной цены и количества товара 
                if instance.buy_price_history is None:
                    transaction.set_rollback(True)
                    return self.htmx_toast_error('Вы не указали цену на гарантийное списание.')
                if instance.quantity_history is None:
                    transaction.set_rollback(True)
                    return self.htmx_toast_error('Вы не указали количество товара на списание.')
                    
                # Записывается (привязывается) юзер
                instance.user = request.user    
                    
                # Количество товара, КОТОРЫЙ УЧАВСТВУЕТ В ОПЕРАЦИИ (запоминание в переменную)
                current_remainder_instance = instance.quantity_history
                    
                # Меняется количество товара в самом HistoryStorage
                instance.remainder_history = selected_object.remainder - current_remainder_instance
                # Записывается оригинальное название из БД
                instance.name_product_history = selected_object.name_product
                # Записывается оригинальный поставщик из БД
                instance.supplier_history = selected_object.supplier
                # Название типа операции
                instance.type_of_operation_history = "Гарантийный возврат"
                # Айдишник товара привязывается к "Оригинальной БД"
                instance.individual_code_history = selected_object.individual_code
                # Меняется количество товара ПОСЛЕ "операции" в "Оригинальной БД (Storage)"
                selected_object.remainder = selected_object.remainder - current_remainder_instance

                if selected_object.remainder < 0:
                    transaction.set_rollback(True)
                    return self.htmx_toast_error('Товара под гарантийное списание указано больше, чем есть на складе!')
                elif selected_object.remainder == 0:
                    if instance.individual_code_history not in list_to_delete_obj:
                        list_to_delete_obj.append(instance.individual_code_history)
            
                # Меняю баланс в кассе:
                global_garanty_sum += instance.buy_price_history * instance.quantity_history
                
                # Сделал историю операции:
                # Список list_for_add_history_storage позволяет внедрить команды с добавлением обьектов в 1 переменную, и затем в конце
                # создать это множество обьектов!
                list_to_add_finane_history.append(FinanceHistoryInfo(user=request.user, 
                type_of_operation=FinanceHistoryInfo.TypeOfOperation.INCOME, category_of_operation = FinanceHistoryInfo.CategoryOfOperation.WARRANTY,
                number_in_the_operation = instance.buy_price_history * instance.quantity_history, product_name = instance.name_product_history,
                product_code = instance.individual_code_history, supplier = instance.supplier_history,
                comment = f'Возврат товара: {instance.name_product_history}, в кол-ве: {instance.quantity_history}, за {instance.buy_price_history * instance.quantity_history} ₽.')
                )          

                # После всех ОСНОВНЫХ действий добавляю в список list_for_add_history_storage 1 обьект (на каждой итерации)
                # чтобы потом сделать bulk_create(list_for_add_history_storage)
                list_for_add_history_storage.append(instance)

            # Если цикл убавления (гарантийного) произошел успешно, осталось только "закомитить" два списка, вычесть с кассы 
            # актуальную цену закупки, и отдать готовый результат!
            # BULK_CREATE!!!
            FinanceHistoryInfo.objects.bulk_create(list_to_add_finane_history)
            # На уровне F выражения меняю баланс в положительную сторону из-за возврата
            CashAccount.objects.filter(user=request.user).update(money_balance=F('money_balance') + global_garanty_sum)

            # Создаю историю гарантийного списания товаров:
            HistoryStorageInfo.objects.bulk_create(list_for_add_history_storage)

            # Обновляю в StorageInfo только само количество товара (так как ничего другого я не изменял)
            StorageInfo.objects.bulk_update(dict_for_objects.values, ['remainder'])

            # После того как обновил StorageInfo, удаляю те обьекты, которые имеют remainder = 0
            StorageInfo.objects.filter(individual_code__in = list_to_delete_obj).delete()

            if request.headers.get('HX-Request'):
                msg = 'Гарантийное списание прошло успешно. Денежные средства были возвращены в кассу!'
                print(msg)
                messages.success(request, msg)
                response = HttpResponse()
                response['HX-Redirect'] = reverse('filter_and_history_storage')
                return response
                                                    
        except Exception as e:
            # Статус 204 если произошла ошибка
            return self.htmx_toast_error(f'Ошибка: {e}.')
                                                    
                
