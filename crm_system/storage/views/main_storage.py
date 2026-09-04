from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import StorageInfo
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.staticfiles import finders


# Данный класс отвечает за обычный показ склада
@method_decorator(login_required(), name='dispatch') 
class StorageCustomView(TemplateView):

    template_name = 'storage/main-storage.html'

    def get(self, request, *args, **kwargs):

        # Получаю объект из БД для показа уже созданных когда-либо товаров, в том числе актуальных
        storage_actual_items = StorageInfo.objects.filter(
            user=self.request.user
        ).all()

        if storage_actual_items:
            return render(request, self.template_name, {"storage_actual_items" : storage_actual_items })

        return render(request, self.template_name)
                        