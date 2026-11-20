from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.db.models import Sum
from orders.models import Orders, CreateServiceWork


# Данный класс отвечает за показ подсчитанной скидки
@method_decorator([login_required, never_cache], name="dispatch")
class GetTotalCount(View):
    def get(self, request, *args, **kwargs):
        connected_id = request.GET.get("get_id_order")
        get_order = Orders.objects.get(user=request.user, id=connected_id)

        # Сумма всех работ
        get_sum_repair = CreateServiceWork.objects.filter(
            user=request.user, connected_id=connected_id
        ).aggregate(total_sum=Sum("service_price"))

        total_sum_val = get_sum_repair["total_sum"] or 0
        final_price = total_sum_val - (get_order.discount or 0)

        # Возвращаем ровно то, что должно быть внутри спана с итогом
        return HttpResponse(f"{final_price} руб.")
