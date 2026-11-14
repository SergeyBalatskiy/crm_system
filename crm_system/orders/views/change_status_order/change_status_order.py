from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Client
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
from django.db.models import Q, Value
from django.db.models.functions import Concat
from profile_user.models import StatusCategory
from orders.models import Orders, CreateServiceWork
from django.db.models import Sum
from profile_user.models import FormsForOrder


# Данный класс отвечает за показ и изменение категории статуса заказа
@method_decorator([login_required, never_cache], name="dispatch")
class ChangeStatusOrder(View):

    # Отдаю все активные категории, которые есть в БД
    def get(self, request, *args, **kwargs):

        # Получаю айдишник нашего заказа
        get_id_order = request.GET.get("get_id_order")

        # Находимся ли в форме?
        type_of_order = request.GET.get("type_of_order")
        print("Узнал, что получил тип заказа!")

        # Получаю все существующие категории
        get_all_categories = StatusCategory.objects.filter(user=request.user)
        context = {"get_id_order": get_id_order}

        # Добавляю дополнительный фильтр, получая все успешные категории + запись в контекст
        context["success"] = get_all_categories.filter(category="success")
        context["in_process"] = get_all_categories.filter(category="in_process")
        context["finished"] = get_all_categories.filter(category="finished")
        context["deferred"] = get_all_categories.filter(category="deferred")

        if type_of_order:
            context["type_of_order"] = type_of_order
            print(type_of_order)
            return render(
                request, "orders/partials/change_category_in_form.html", context
            )

        return render(request, "orders/partials/change_current_category.html", context)

    # Получает айдишник конкретной актуальной категории, и, делает ее актуальной
    def post(self, request, *args, **kwargs):

        try:
            # Получаю айдишник категории
            get_id_category = request.POST.get("actual_id")

            # Узнаю, находимся ли мы в самой форме? (Получив инфу о типе заказа)
            type_of_order = request.POST.get("type_of_order")

            # Получаю айдишник заказа
            get_id_order = request.POST.get("get_id_order")

            # Получаю категорию из БД
            get_selected_category = StatusCategory.objects.get(
                user=request.user, id=get_id_category
            )

            # Беру сам заказ, чтобы в нем обновить статус
            update_category = Orders.objects.select_for_update().get(
                user=request.user, id=get_id_order
            )

            # Обновляю в заказе цвет, название и eng_name категории
            update_category.name_category = get_selected_category.name
            update_category.color_category = get_selected_category.color
            update_category.category_eng = get_selected_category.category
            update_category.save()

            # Получаю множество заказов, где имеется статус : "Новый"
            get_order = Orders.objects.filter(user=request.user)
            # Счетчик для показа только новых заказов:
            new_counts = len(get_order.filter(user=request.user, category_eng="new"))

            # Если категория == ВЫДАН, то закрываем сайдбар + показываем предложение об оплате
            if get_selected_category.name == "Выдан":
                print("ВЫБРАЛИ СТАТУС Выдан")
                # Получение итоговой суммы ремонта:
                get_sum_repair = CreateServiceWork.objects.filter(
                    user=self.request.user, connected_id=get_id_order
                ).aggregate(total_sum=Sum("service_price"))
                get_sum_repair = get_sum_repair["total_sum"] or 0
                total_price = get_sum_repair - get_order.get(id=get_id_order).discount

                # Получаю имя клиента для дальнейшей отправки
                get_name_client = update_category.client.name

                pay_context = {
                    "get_order": update_category,
                    "summary_price": total_price,
                    "client_name": get_name_client,
                }

                response = render(
                    request, "orders/partials/show_process_pay.html", pay_context
                )

                # Обновление визуальной составляющей на главной странице + в самой форме
                response["HX-Trigger"] = json.dumps(
                    {
                        "refreshOrders": True,
                        "updateNewCounter": new_counts,
                        "closeClientDrawer": True,
                    }
                )
                print("Дошли до сюда")
                return response

            # Если категория другая, и если у нас есть тип заказа, значит что нужно отдавать шаблон с новым статусом
            if type_of_order:
                print("Сработал этот блок!")
                print("у нас есть тип заказа")
                get_order = get_order.filter(id=get_id_order).first()
                get_original_form = FormsForOrder.objects.filter(
                    user=request.user, type_of_order=type_of_order
                ).first()
                print(get_original_form)
                sections = get_original_form.json_forms.get("sections", [])

                saved_data = get_order.form_with_order_information.get("order_dict", [])
                saved_map = {block["id"]: block for block in saved_data}

                for section in sections:
                    sec_id = section.get("id")
                    sec_saved_values = saved_map.get(sec_id, {})
                    for field in section.get("fields"):
                        f_key = field.get("field_key")
                        field["value"] = sec_saved_values.get(f_key)
                context = {
                    "get_id_order": get_id_order,
                    "get_order": get_order,
                    "sections": sections,
                    "current_type": get_order.type_of_order,
                    "save_success": True,
                }
                response = render(
                    request, "orders/show_getted_order/show_getted_form.html", context
                )

                # Запрос на обновление основного поля с нашими заказами
                response["HX-Trigger"] = json.dumps(
                    {"refreshOrders": True, "updateNewCounter": new_counts}
                )
                return response

            response = HttpResponse(status=204)
            # Запрос на обновление основного поля с нашими заказами
            response["HX-Trigger"] = json.dumps(
                {"refreshOrders": True, "updateNewCounter": new_counts}
            )
            return response

        # Хочу тут как то выводить если случится какая то ошибка...
        except Exception as e:
            msg = f"Ошибка: {e}"
            print(msg)
            return HttpResponse(msg, status=400)
