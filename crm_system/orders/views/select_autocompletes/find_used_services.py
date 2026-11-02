from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from services.models import ServicesInfo
from dal_select2.views import Select2QuerySetView
from django.db.models import Q, TextField
from django.db.models.functions import Cast

@method_decorator(login_required(), name='dispatch') 
class ServicesSelectAutocomplete(Select2QuerySetView):
    def get_queryset(self): 
        qs = ServicesInfo.objects.filter(user=self.request.user).order_by('-id')
        if self.q:
            qs = qs.annotate(
                price_str=Cast('price', output_field=TextField())
            )
            
            qs = qs.filter(
                Q(name_service_work__icontains=self.q) | 
                Q(category__icontains=self.q) | 
                Q(price_str__icontains=self.q)
            )
        return qs

    def get_results(self, context):
            return [
                {
                    'id': self.get_result_value(result), 
                    'text': f"Услуга: {result.name_service_work or '-'} | Категория: {result.category} | Цена: {result.price}",
                    'name': result.name_service_work,
                   
                }
                for result in context['object_list']
            ]