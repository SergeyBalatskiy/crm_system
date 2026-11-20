from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q, TextField
from django.db.models.functions import Cast

@method_decorator(login_required(), name='dispatch') 
class CountryAutocomplete(Select2QuerySetView):
    def get_queryset(self): 
        qs = StorageInfo.objects.filter(user=self.request.user).order_by('-individual_code')
        if self.q:
            qs = qs.annotate(
                buy_price_str=Cast('buy_price', output_field=TextField()),
                individual_code_str=Cast('individual_code', output_field=TextField())
            )
            qs = qs.filter(
                Q(name_product__icontains=self.q) | 
                Q(individual_code_str__icontains=self.q) | 
                Q(buy_price_str__icontains=self.q) | 
                Q(supplier__icontains=self.q)
            )
        return qs

    def get_results(self, context):
            
            return [
                 
                {
                    'id': self.get_result_value(result), 
                    'text': f"Код: {result.individual_code or '-'} | Товар: {result.name_product} | Поставщик: {result.supplier or '-'}",
                    'name': result.name_product,
                    'code': result.individual_code or '-',
                    'supplier': result.supplier or '',
                    # Явное приведение Decimal к int / float
                    'price': int(result.retail_price) if result.retail_price else 0,
                    'remainder': result.remainder if result.remainder is not None else '-',
                }
                
                for result in context['object_list']
                
            ]