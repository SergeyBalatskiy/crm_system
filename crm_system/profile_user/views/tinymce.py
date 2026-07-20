from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.forms import ServiceInfoForm, WorkersFormSet, DocumentInfoForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from profile_user.models import StatusCategory, DocumentInformation, WorkersInfo



# Данный класс отвечает за отображение tinymce (GET запрос) и принятие из формы в метод POST (POST запрос)
@method_decorator(login_required(), name='dispatch')
class ShowDocumentView(TemplateView):
    template_name = 'profile_user/tinymce.html'

    # Передаю в сайт методом GET форму самого tinymce
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)