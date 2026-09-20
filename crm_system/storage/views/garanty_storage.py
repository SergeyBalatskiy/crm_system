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

# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator([never_cache, login_required], name='dispatch') 
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
                    messages.error(request, 'Пожалуйста, выберите хотя бы один товар на списание!')
                    return render(request, 'storage/messages.html')
                    
                # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
                for instance in instances:
                    history_data = StorageInfo.objects.filter(individual_code=instance.individual_code_history).first() 

                    if history_data is None:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        messages.error(request, f'Ошибка: вы попытались повторно списать товар с кодом {instance.name_product_history}, количество которого на момент прошлого списания уже стало 0.')
                        return render(request, 'storage/messages.html')

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
                                transaction.set_rollback(True)
                                messages.error(request, f'Вы не указали цену товара на списание')
                                return render(request, 'storage/messages.html')

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
                            messages.error(request, f'Товара {history_data.name_product} на складе меньше, чем вы указали под списание.')
                            return render(request, 'storage/messages.html')
                                                    
                    except Exception as e:
                        # Статус 204 если произошла ошибка + транзакция
                        transaction.set_rollback(True)
                        messages.error(request, f'Ошибка: {e}.')
                        return render(request, 'storage/messages.html')
                                                     

                if request.headers.get('HX-Request'):
                    msg = 'Гарантийное списание прошло успешно. Денежные средства были возвращены в кассу!'
                    print(msg)
                    messages.success(request, msg)
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('filter_and_history_storage')
                    return response

            # Статус 204 если ошибка
            if request.headers.get('HX-Request'):
                messages.error(request, f'Пожалуйста, проверьте поля на корректность ввода и повторите попытку.')
                return render(request, 'storage/messages.html')
                                                