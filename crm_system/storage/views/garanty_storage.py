from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo
from django.shortcuts import render
from storage.forms import GarantyHistoryForm


# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator(login_required(), name='dispatch') 
class StorageGarantyCustomView(TemplateView):

    template_name = 'storage/garanty-storage.html'

    def post(self, request, *args, **kwargs):
        ...
        
    def get(self, request, *args, **kwargs):
        # Получаю форму для добавления товара
        formset = GarantyHistoryForm(queryset=HistoryStorageInfo.objects.none())
        return render(request, self.template_name, {'form_garanty' : formset})
                                        