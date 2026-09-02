from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.models import DocumentInformation
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.staticfiles import finders


# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator(login_required(), name='dispatch') 
class StorageRemovalCustomView(TemplateView):

    template_name = 'storage/removal-storage.html'

    def post(self, request, *args, **kwargs):
        ...
        
    def get(self, request, *args, **kwargs):
        return render(self.request, self.template_name)
                                 