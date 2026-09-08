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
class FormRemovalCustomView(TemplateView):

    template_name = 'storage/form-removal.html'

    def get(self, request, *args, **kwargs):

        if request.headers.get('HX-Request') == 'true':
            print("Вызвали get-HTMX запрос на отображение формы (Гарантийной или просто списание)")
            type_of_form_selected = request.GET.get('type_of_form_selected')

            if type_of_form_selected == 'warranty_form':
                return render('garanty-storage')
            return render('removal-storage')

        return render(request, self.template_name)
