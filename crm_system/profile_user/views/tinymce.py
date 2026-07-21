from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.forms import ServiceInfoForm, WorkersFormSet, DocumentInfoForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from profile_user.models import StatusCategory, DocumentInformation, WorkersInfo
from django.http import HttpResponse


# Данный класс отвечает за отображение tinymce (GET запрос) и принятие из формы в метод POST (POST запрос)
@method_decorator(login_required(), name='dispatch')
class ShowDocumentView(TemplateView):
    documents_form = 'profile_user/documents_form/document.html'
    template_name = 'profile_user/tinymce.html'

    def form_valid(self, document_info, name):
        upd_doc = DocumentInformation.objects.get(user = self.request.user, name = name)
        upd_doc.content = document_info.cleaned_data["content"]
        upd_doc.save()
        return HttpResponse(status=204)

    def post(self, request, *args, **kwargs):
        cur_doc = request.POST.get('document')

        document_names = {
            'garanty_doc': 'Акт о гарантии',
            'adoption_doc': 'Акт о принятии',
            'cancell_doc': 'Акт о отказе',
            'complete_doc': 'Акт о выполненных работах'
        }

        name = document_names.get(cur_doc)
        document_info = DocumentInfoForm(self.request.POST)
        if document_info.is_valid():
                # Здесь активируется функция, которая отвечает за главное сохранение
                return self.form_valid(document_info, name)

    # Передаю в сайт методом GET форму самого tinymce
    def get(self, request, *args, **kwargs):
        
        # Проверяю, что за метод получения информации с сайта?
        # Если он сделан через HTMX, то:
        if request.headers.get('HX-Request') == 'true':
            # Используя name="documents" value="" я получаю то, какой документ нужен из формы GET запроса
            document_selected = request.GET.get('documents')

            document_names = {
            'garanty_doc': 'Акт о гарантии',
            'adoption_doc': 'Акт о принятии',
            'cancell_doc': 'Акт о отказе',
            'complete_doc': 'Акт о выполненных работах'
        }
            # По ключу получаю то, что запрашивают
            name = document_names.get(document_selected)

            if name:
                # Получаю обьект (ВЕСЬ)
                document = DocumentInformation.objects.filter(name=name, user = self.request.user).first()
                # У этого ОБЬЕКТА беру только content
                content = document.content

                # ОТДАЮ И название, и текст
                return render(request, 'profile_user/documents_form/document.html', {'content': content, 'cur_doc': document_selected})
            
        # Если метод получения информации без HTMX, то сначала необходимо загрузить форму (только 1 раз)
        # потом отобразить текст и скрыто передать форму для "фальстарта"
        form = DocumentInfoForm()
        html_fragment = "Пока что вы не выбрали ни одну форму"
        return render(request, self.template_name, {'message': html_fragment, 'tiny_mce': form } )
