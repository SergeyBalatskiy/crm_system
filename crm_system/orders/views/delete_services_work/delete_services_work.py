from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from services.models import ServicesInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from orders.models import CreateServiceWork
from django.db.models import Sum
from storage.models import StorageInfo
from orders.forms import WorkCreatingForm
from django.shortcuts import render

# Данный класс отвечает за удаление определенной работы, которая привязана к самому заказу
@method_decorator(login_required(), name='dispatch') 
class DeleteServicesInOrder(Select2QuerySetView):

    # Необходимо улавливать запрос с айдишником работы и удалять его
    def post(self, request, *args, **kwargs):

        # Получаю все остальное:

        # Получаю форму
        create_work_form = WorkCreatingForm()

        # Получаю айди конкретного заказа показа всех работ именно у него
        connected_id = request.POST.get('get_id_order')
        get_created_works_later = CreateServiceWork.objects.filter(user=request.user, connected_id=connected_id).order_by('service_was_created')

        # Получаю уникальный айдишник нужной для удаления работы 
        get_id_to_delete = request.POST.get('id_service_work')

        # Получаю сам обьект для дальнейшего его удаления
        find_service_work = CreateServiceWork.objects.filter(user=request.user, id=get_id_to_delete)

        # Если обьект есть:
        if find_service_work.exists():
            # Получение итоговой суммы ремонта
            get_sum_repair = CreateServiceWork.objects.filter(user=self.request.user, connected_id = connected_id).aggregate(total_sum=Sum('service_price'))
            total_price = get_sum_repair['total_sum']

            # Беру нужный обьект из бд после фильтрации
            find_service_work = find_service_work.get()

            # Если у нас найдется действующий товар на складе, значит, к нему можно добавить количество списанного
            if StorageInfo.objects.filter(user=request.user, individual_code = find_service_work.detail_id).exists():
                get_to_update = StorageInfo.objects.select_for_update().get(user=request.user, individual_code = find_service_work.detail_id)
                get_to_update.remainder = get_to_update.remainder + find_service_work.quantity_was_used
                get_to_update.save()

            else:
                # Если обьекта нету, значит, нужно его создать...
                created_returned_detail = StorageInfo.objects.create(user=request.user, name_product = find_service_work.detail_name_was_used, quantity_at_the_purchase = service_work.detail_quantity_was_buyed,
                    supplier = find_service_work.detail_supplier, buy_price = find_service_work.detail_buy_price, retail_price = find_service_work.detail_retail_price,
                    minimum_items_for_notification = find_service_work.detail_minimum_items_for_not, remainder = find_service_work.quantity_was_used,
                )
                # Записываем айдишник (individual_code) + сохраняем
                created_returned_detail.individual_code = created_returned_detail.id
                created_returned_detail.save()

            # СДЕЛАТЬ ТУТ ОБЩУЮ ЛОГИКУ ДОБАВЛЕНИЯ ИСТОРИИ ПОСТУПЛЕНИЯ ТОВАРА ОБРАТНО
            create_history = ...

            # После всех манипуляций - удаляем окончательно нашу работу
            find_service_work.delete()
            msg = ''
        else:
            msg = 'Произошла ошибка. Повторите попытку позже!'

        return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
        'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id, 'total_price' : total_price, 'msg' : msg})
