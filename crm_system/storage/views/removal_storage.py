from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo, StorageInfo
from django.shortcuts import render, redirect
from storage.forms import RemovalHistoryForm
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
import json
from django.db import transaction
from django.urls import reverse

# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator(login_required(), name='dispatch') 
class StorageRemovalCustomView(TemplateView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Получаю все формсеты, которые есть
        formset = RemovalHistoryForm(request.POST)
        
        # Валидация форм (пропуск не важных полей) + сохранение важных
        if formset.is_valid():
        
            # Остановка сохранения 
            instances = formset.save(commit=False)

            if not instances:
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=204)
                    payload = {
                            'showMessage': 'Пожалуйста, выберите хотя бы один товар на списание!'
                        }
                    response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                    return response

            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            for instance in instances:
                try:
                    history_data = StorageInfo.objects.filter(individual_code=instance.individual_code_history).first()
                    instance.user = request.user

                    if history_data is None:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        if request.headers.get('HX-Request'):
                            response = HttpResponse(status=204)
                            payload = {'showMessage': f'Ошибка: в предыдущем списании вы убрали все возможное количество товара!'}
                            response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                            return response

                    instance.name_product_history = history_data.name_product
                    instance.type_of_operation_history = "Возврат без возмещения денежных средств"
                    instance.individual_code_history = history_data.individual_code
                    current_remainder_instance = instance.quantity_history

                    # Проверяю на "верность" введенного количества товара:
                    if history_data.remainder - current_remainder_instance < 0:
                        # Статус 204 если произошла ошибка + транзакция
                            transaction.set_rollback(True)
                            if request.headers.get('HX-Request'):
                                response = HttpResponse(status=204)
                                payload = {'showMessage': f'Ошибка: товара {history_data.name_product} на складе меньше, чем вы указали под списание!'}
                                response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                                return response

                    instance.remainder_history = history_data.remainder - current_remainder_instance
                    history_data.remainder = history_data.remainder - current_remainder_instance
                    instance.time_created_history = history_data.created_at
                    instance.buy_price_history = 0
                    instance.time_of_operation_history = timezone.now()
                    instance.save()
                    # Обновляю обьект (один) в StorageInfo, чтобы его впоследствии и брать, и взаимодействовать.
                    history_data.save()
                    if history_data.remainder == 0:
                        history_data.delete()

                except Exception as e:
                    # Статус 204 если произошла ошибка + транзакция
                    transaction.set_rollback(True)
                    if request.headers.get('HX-Request'):
                        response = HttpResponse(status=204)
                        payload = {'showMessage': f'Ошибка списания: {e}'}
                        response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                        return response
                    
            if request.headers.get('HX-Request'):
                    msg = 'Списание товара без возмещения средств прошло успешно!'
                    messages.success(request, msg)
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('history-storage')
                    return response 
                
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            payload = {'showMessage': f'Ошибка списания: указано товаров болше, чем есть на складе!'}
            response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
            return response