from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import HistoryStorageInfo, StorageInfo
from django.shortcuts import render, redirect
from storage.forms import RemovalHistoryForm
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.urls import reverse
import json
from django.views.decorators.cache import never_cache

# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator([never_cache, login_required], name='dispatch') 
class StorageRemovalCustomView(TemplateView):

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
        formset = RemovalHistoryForm(request.POST)

        # Валидация формсетов
        if not formset.is_valid():
            return self.htmx_toast_error('Пожалуйста, проверьте поля на корректность ввода и повторите попытку!')
             
        # Остановка сохранения 
        instances = formset.save(commit=False)
        # Обработка еще одного некорректного случая:
        if not instances:
            return self.htmx_toast_error('Пожалуйста, выберите хотя бы один товар на списание!')
            
        # Список на добавление истории операции гарантийного возврата
        list_for_add_history_storage = []

        # Список товаров, количество которых равно 0!
        list_to_delete_object = []

        try:
            # Получаю только айди товаров исходя из формсетов
            codes = [i.individual_code_history for i in instances]
            # Получаю QuerySet`ы и упаковываю их в словарь (1 запрос в БД)
            dict_for_objects = {s.individual_code:s for s in StorageInfo.objects.select_for_update().filter(user=request.user, individual_code__in=codes)}
                
            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            for instance in instances:

                # Получаю 1 обьект из словаря с StorageInfo - Query`сетами
                selected_object = dict_for_objects.get(instance.individual_code_history)

                # Если такого товара нету в БД: 
                if not selected_object:
                    return self.htmx_toast_error('Такого товара не существует в БД!')

                instance.user = request.user
                instance.name_product_history = selected_object.name_product
                instance.type_of_operation_history = "Возврат без возмещения денежных средств"
                instance.individual_code_history = selected_object.individual_code
                current_remainder_instance = instance.quantity_history
                instance.remainder_history = selected_object.remainder - current_remainder_instance
                selected_object.remainder = selected_object.remainder - current_remainder_instance
                instance.buy_price_history = 0
                instance.time_of_operation_history = timezone.now()

                # Проверяю на "верность" введенного количества товара:
                if selected_object.remainder < 0:
                    transaction.set_rollback(True)
                    return self.htmx_toast_error('Товара под списание указано больше, чем есть на складе!')
                elif selected_object.remainder == 0:
                    list_to_delete_object.append(instance.individual_code_history)

                # После всех ОСНОВНЫХ действий добавляю в список list_for_add_history_storage 1 обьект (на каждой итерации)
                # чтобы потом сделать bulk_create(list_for_add_history_storage)
                list_for_add_history_storage.append(instance)
            
            # Если цикл убавления (гарантийного) произошел успешно, осталось только "закомитить" два списка
            # BULK_CREATE!!!
            # (2 запрос)
            # Создаю историю гарантийного списания товаров: 
            HistoryStorageInfo.objects.bulk_create(list_for_add_history_storage)

            # (3 запрос)
            # Обновляю в StorageInfo только само количество товара (так как ничего другого я не изменял)
            StorageInfo.objects.bulk_update(dict_for_objects.values(), ['remainder'])
            
            # (4 запрос)
            # После того как обновил StorageInfo, удаляю те обьекты, которые имеют remainder = 0
            StorageInfo.objects.filter(user = request.user, individual_code__in = list_to_delete_object).delete()

            if request.headers.get('HX-Request'):
                msg = 'Списание товара без возмещения средств прошло успешно!'
                messages.success(request, msg)
                response = HttpResponse()
                response['HX-Redirect'] = reverse('filter_and_history_storage')
                return response 
                        
        except Exception as e:
            transaction.set_rollback(True)
            return self.htmx_toast_error(f'Ошибка: {e}')