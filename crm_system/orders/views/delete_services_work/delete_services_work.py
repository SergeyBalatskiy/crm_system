from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from services.models import ServicesInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from orders.models import CreateServiceWork
from django.db.models import Sum
from orders.forms import WorkCreatingForm
from django.shortcuts import render

# Данный класс отвечает за удаление определенной работы, которая привязана к самому заказу
@method_decorator(login_required(), name='dispatch') 
class DeleteServicesInOrder(Select2QuerySetView):

    # Необходимо улавливать запрос с айдишником работы и удалять его
    def post(self, request, *args, **kwargs):

        # Получаю все остальное:
        create_work_form = WorkCreatingForm()
        connected_id = request.POST.get('get_id_order')
        get_created_works_later = CreateServiceWork.objects.filter(user=request.user, connected_id=connected_id).order_by('service_was_created')

        # Получаю обьект с названием работы 
        get_id_to_delete = request.POST.get('id_service_work')

        # Получаю сам обьект
        service_work = CreateServiceWork.objects.filter(user=request.user, id=get_id_to_delete)

        # Если обьект есть:
        if service_work.exists():
            service_work.delete()
            # Получение суммы итоговой ремонта
            get_sum_repair = CreateServiceWork.objects.filter(user=self.request.user, connected_id = connected_id).aggregate(total_sum=Sum('service_price'))
            total_price = get_sum_repair['total_sum']

            msg = ''
        else:
            msg = 'Произошла ошибка. Повторите попытку позже!'

        return render(self.request, 'orders/show_work_success/show_work.html', {'create_work_form' : create_work_form, 
        'get_created_works_later' : get_created_works_later, 'connected_id' : connected_id, 'total_price' : total_price, 'msg' : msg})
