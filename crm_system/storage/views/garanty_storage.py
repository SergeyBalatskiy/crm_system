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
import json
from django.urls import reverse
from django.db import transaction

# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator(login_required(), name='dispatch') 
class StorageGarantyCustomView(TemplateView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
            # Получаю все формсеты, которые есть
            formset = GarantyHistoryForm(request.POST)
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
                    history_data = StorageInfo.objects.filter(individual_code=instance.individual_code_history).first() 

                    if history_data is None:

                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        if request.headers.get('HX-Request'):
                            response = HttpResponse(status=204)
                            payload = {
                                'showMessage': f'Ошибка: в предыдущем списании вы убрали все возможное количество товара!'
                            }
                            response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                            return response

                    # Записывается (привязывается) юзер
                    instance.user = request.user

                    try:
                        # Количество товара, КОТОРЫЙ УЧАВСТВУЕТ В ОПЕРАЦИИ (запоминание в переменную)
                        current_remainder_instance = instance.quantity_history

                        # Проверка на наличие введенной цены и количества товара
                        if (instance.buy_price_history is None) or (instance.quantity_history is None):
                            # Статус 204 если произошла ошибка + транзакция
                            transaction.set_rollback(True)
                            if request.headers.get('HX-Request'):
                                response = HttpResponse(status=204)
                                payload = {
                                    'showMessage': f'Ошибка: Вы не указали цену товара!'
                                }
                                response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                                return response

                        # Записывается количество товара который учавствует в "операции"
                        # с проверкой на то, что товара не будет отрицателтьное количество!
                        if history_data.remainder - current_remainder_instance >=0:  # Если количество товара НА удаление МЕНЬШЕ или РАВНО фактическому 
                            # Меняется количество товара в самом HistoryStorage
                            instance.remainder_history = history_data.remainder - current_remainder_instance
                            # Записывается оригинальное название из БД
                            instance.name_product_history = history_data.name_product
                            # Записывается оригинальный поставщик из БД
                            instance.supplier_history = history_data.supplier
                            # Название типа операции
                            instance.type_of_operation_history = "Гарантийный возврат"
                            # Айдишник товара привязывается к "Оригинальной БД"
                            instance.individual_code_history = history_data.individual_code
                            # Меняется количество товара ПОСЛЕ "операции" в "Оригинальной БД (Storage)"
                            history_data.remainder = history_data.remainder - current_remainder_instance
                            if history_data.remainder == 0: # Если количество товара РАВНО 0:
                                # Дата поступления данного товара на склад
                                instance.time_created_history = history_data.created_at
                                # Дата проведения "операции"
                                instance.time_of_operation_history = timezone.now()
                                instance.save()
                         
                                history_data.delete()
                            else:  # Если количество товара БОЛЬШЕ 0:
                                # Дата поступления данного товара на склад
                                instance.time_created_history = history_data.created_at
                                # Дата проведения "операции"
                                instance.time_of_operation_history = timezone.now()
                                instance.save()
                                # Обновляю обьект (один) в StorageInfo, чтобы его впоследствии и брать, и взаимодействовать.
                                history_data.save()
                
                        else: # Если количество товара НА удаление БОЛЬШЕ чем фактическое количество:
                            # Статус 204 если произошла ошибка + транзакция
                            transaction.set_rollback(True)
                            if request.headers.get('HX-Request'):
                                response = HttpResponse(status=204)
                                payload = {
                                    'showMessage': f'Ошибка: Товара {history_data.name_product} на складе меньше, чем вы указали под списание.'
                                }
                                response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                                return response
                                                    
                    except Exception as e:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        if request.headers.get('HX-Request'):
                            response = HttpResponse(status=204)
                            payload = {
                                'showMessage': f'Ошибка: {e}'
                            }
                            response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                            return response

                if request.headers.get('HX-Request'):
                    msg = 'Гарантийное списание прошло успешно. Денежные средства были возвращены в кассу!'
                    print(msg)
                    messages.success(request, msg)
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('history-storage')
                    return response

            # Статус 204 если ошибка
            if request.headers.get('HX-Request'):
                # Собираем список всех ошибок из формсета
                error_details = []
                
                # Ошибки уровня всего формсета (например, некорректный TOTAL_FORMS)
                if formset.non_form_errors():
                    error_details.append(f"Формсет: {', '.join(formset.non_form_errors())}")

                # Ошибки конкретных полей по каждой строке
                for index, form_errors in enumerate(formset.errors):
                    if form_errors:
                        fields_with_errors = [f"{field}: {', '.join(errs)}" for field, errs in form_errors.items()]
                        error_details.append(f"Строка {index + 1} -> {'; '.join(fields_with_errors)}")

                msg = " | ".join(error_details) if error_details else "Ошибка валидации данных."

                response = HttpResponse(status=204)
                payload = {'showMessage': f'Ошибка: {msg}'}
                response['HX-Trigger'] = json.dumps(payload, ensure_ascii=True)
                return response