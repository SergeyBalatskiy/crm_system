from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q

""" Суть данной вью заключается в том, что она автоматически и моментально после ввода каждого
символа пользователя, предлагает ему актуальные по его вводу обьекты/обьект из БД """

# Данный класс отвечает за отображение автоподсказок
@method_decorator(login_required(), name='dispatch') 
class CountryAutocomplete(Select2QuerySetView):
    # Обязательная функция, которая выдает результатом "готовые обьекты" на автозаполнение
    def get_queryset(self):
        # Переменная, которая если не заполнена, то выдает ВСЕ обьекты
        qs = StorageInfo.objects.filter(user=self.request.user)
        # Если имеется хоть 1 символ в поле, то выдается результат с учетом поля _istartswith без
        # зависимости от регистра
        if self.q:
            qs = qs.filter(
                Q(name_product__istartswith=self.q) | Q(individual_code__istartswith=self.q) | Q(buy_price__istartswith=self.q) | Q(supplier__istartswith=self.q)
            )

        return qs

    def get_results(self, context):
        # Отдает в режиме реального времени на HTML правильно отформатированные данные для дальнейшей вставки
        return [
            {
            'id' : self.get_result_value(result), 
            'text' : f"{result.name_product} | Код: {result.individual_code or '-'} | Поставщик: {result.supplier or '-'}",
            'name' : result.name_product,
            'code' : result.individual_code or '-',
            'supplier' : result.supplier or '',
            'price' : result.buy_price or 0,
            }
            for result in context['object_list']
        ]
    