from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Client, CreateServiceWork
from services.forms import ServicesWorkForm
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timedelta
import json
from django.db.models.functions import Cast
from django.shortcuts import render
from profile_user.models import WorkersInfo
from orders.forms import WorkCreatingForm
from django.db.models import Q, Value
from django.db.models.functions import Concat
from storage.models import StorageInfo, HistoryStorageInfo

# Данный класс отвечает за показ существующих "рабочих" (Обращение в воркерс и показ)
@method_decorator([login_required, never_cache], name='dispatch') 
class ServiceWorkCreate(View):

    # Здесь активируется функция, которая уже сохраняет оказываемую работу в базу данных CreateServiceWork
    def form_valid(self, get_one_form, get_id_order):

        get_created_works_later = CreateServiceWork.objects.filter(user=self.request.user, connected_id=get_id_order).order_by('service_was_created')
        create_work_form = WorkCreatingForm()
        connected_id = get_id_order

        try:
            with transaction.atomic():

                # Остановка сохранения и запись самого обьекта в переменную (с ней мы будем работать для дальнейшего сохранения в БД)
                create_work_completed = get_one_form.save(commit=False)

                # Проверяю есть ли у меня код товара (если есть, то логика такая : создание, удаление, история)
                if create_work_completed.detail_id:
                    get_id_from_storage = create_work_completed.detail_id
                    # Беру обьект
                    selected_detail_storage = StorageInfo.objects.select_for_update().get(user=self.request.user, id=get_id_from_storage)
                    create_work_completed.detail_buy_price = selected_detail_storage.buy_price
                    create_work_completed.detail_retail_price = selected_detail_storage.retail_price
                    create_work_completed.detail_minimum_items_for_not = selected_detail_storage.minimum_items_for_notification
                    create_work_completed.detail_supplier = selected_detail_storage.supplier
                    create_work_completed.detail_quantity_was_buyed = selected_detail_storage.quantity_at_the_purchase

                    # Сохраняю ссылку на пользователя и связываю с айди
                    create_work_completed.connected_id = get_id_order
                    create_work_completed.user = self.request.user

                    # Тут проверяю, хватает ли нам товара на складе (чтобы не было отрицательного списания + если списание равно 0 то
                    # мы должны удалить товар)
                    count_remainder = selected_detail_storage.remainder - get_one_form.cleaned_data['quantity_was_used']

                    # Если при списании товара оказалось, что задействовано больше деталей, чем есть на складе, то выдаем ошибку
                    if count_remainder < 0:
                        transaction.set_rollback(True)
                        msg = 'Нельзя списать товара больше, чем есть на складе!'
                        print(msg)
                        return render(self.request, 'orders/show_work_success/show_work.html', {'msg' : msg})

                    # Если при списании товара со склада, количество оказалось равно нулю, то:
                    elif count_remainder == 0:
                        # Списываю с хранилища (удаляю) обьект + создаю историю удаления:
                        create_history_deleted = HistoryStorageInfo(user = self.request.user, type_of_operation_history = 'Списание', 
                        name_product_history = selected_detail_storage.name_product, individual_code_history = selected_detail_storage.individual_code,
                        quantity_history = get_one_form.cleaned_data['quantity_was_used'], buy_price_history = selected_detail_storage.buy_price, 
                        supplier_history = selected_detail_storage.supplier, remainder_history = 0)

                        # Сохраняю
                        create_history_deleted.save()

                        # Сохраняю созданный обьект в БД
                        create_work_completed.save()

                        # Удаляю
                        selected_detail_storage.delete()
                        print('Был последний товар, он списан и удален, вернул ничего, все прошло успешно')

                        return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
                        'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id})

                    # Если при списании у нас товара больше нуля (1, 2, 5, 20, ...)
                    else:
                        create_history_deleted = HistoryStorageInfo(user = self.request.user, type_of_operation_history = 'Списание', 
                        name_product_history = selected_detail_storage.name_product, individual_code_history = selected_detail_storage.individual_code,
                        quantity_history = get_one_form.cleaned_data['quantity_was_used'], buy_price_history = selected_detail_storage.buy_price, 
                        supplier_history = selected_detail_storage.supplier, remainder_history = count_remainder)
                    
                        # Сохраняю созданный обьект в БД
                        create_work_completed.save()

                        create_work_completed.user = self.request.user
                        create_work_completed.connected_id = get_id_order
                        create_work_completed.save() 

                        print('На складе еще остался товар, история списания создана и сохранена')

                        # Ничего не возвращает так как мы просто создали оказываемую услугу
                        return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
                        'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id})
                
                # Если айди нету, то просто сохраняю
                else: 
                    create_work_completed.user = self.request.user
                    create_work_completed.connected_id = get_id_order
                    create_work_completed.save() 

                    print('Ничего не было выбрано, просто обычное создание текста без использования детали')

                    return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
                    'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id})
                    
        except Exception as e:
                msg = f'Произошла ошибка: {e}'
                # Выдает ошибку
                print(msg)
                return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
                'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id, 'error_message' : msg})

    def get(self, request, *args, **kwargs):

        # Получаю сигнал на запрос показа еще одного бокового окна которое вылезает дополнительно и отображает ход работ
        # + получаю специально код самого заказа
        connected_id = request.GET.get('get_id_order')

        # Плюс дополнительно если человек открывает разметку не в первый раз и там уже есть выполненные работы, то я иду в БД
        # и фильтрую по тому, что есть + с сортировкой по дате (от старого к новому)
        get_created_works_later = CreateServiceWork.objects.filter(user=request.user, connected_id=connected_id).order_by('service_was_created')

        # Беру форму с созданием названия работы, цены, (возможно названия детали и количества ее использования)
        create_work_form = WorkCreatingForm()
        return render(request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id})

    def post(self, request, *args, **kwargs):

        # Получаю обьект с названием работы 
        get_one_form = WorkCreatingForm(data=self.request.POST)

        # Получаю код заказа (чтобы можно было связать с заказом)
        get_id_order = request.POST.get('get_id_order')

        if get_one_form.is_valid():

            service_provided = get_one_form.cleaned_data['service_provided']
            quantity_was_used = get_one_form.cleaned_data['quantity_was_used']

            return self.form_valid(get_one_form, get_id_order)

        # Показываем на текущем шаблоне форму, в случае если она не валидна
        print('Вернул респонс')
        return HttpResponse(status=204)
