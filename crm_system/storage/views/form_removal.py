from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import StorageInfo, HistoryStorageInfo
from django.http import HttpResponse
from django.shortcuts import render
from storage.forms import RemovalHistoryForm, GarantyHistoryForm
from django.contrib.staticfiles import finders


# Данный класс отвечает за обычный показ склада
@method_decorator(login_required(), name='dispatch') 
class FormRemovalCustomView(TemplateView):

    garanty_template_name = 'storage/garanty/garanty-storage.html'
    template_name = 'storage/form-removal.html'
    removal_template_name = 'storage/removal/removal-storage.html'

    def get(self, request, *args, **kwargs):

        if request.headers.get('HX-Request') == 'true':
            type_of_form_selected = request.GET.get('type_of_form_selected')

            if type_of_form_selected == 'warranty_form':
                # Получаю гарантийную форму для списания товара с возмещением компенсации
                formset = GarantyHistoryForm(queryset=HistoryStorageInfo.objects.none())
                return render(request, self.garanty_template_name, {'form_garanty' : formset})

            # Получаю форму для списания товара без возмещения компенсации
            formset = RemovalHistoryForm(queryset=HistoryStorageInfo.objects.none())
            return render(request, self.removal_template_name, {'form_removal' : formset})

        return render(request, self.template_name)
