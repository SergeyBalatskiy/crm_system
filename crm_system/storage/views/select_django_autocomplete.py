from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from dal_select2.views import Select2QuerySetView

# Данный класс отвечает за отображение автоподсказок
@method_decorator(login_required(), name='dispatch') 
class CountryAutocomplete(Select2QuerySetView):

    def get_queryset(self):

        qs = StorageInfo.objects.filter(user=self.request.user)

        if self.q:
            qs = qs.filter(name_product__istartswith=self.q)

        return qs