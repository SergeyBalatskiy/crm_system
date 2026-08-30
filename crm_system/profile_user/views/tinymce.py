from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.forms import DocumentInfoForm
from profile_user.models import DocumentInformation
from django.http import HttpResponse


# Данный класс отвечает за отображение tinymce (GET запрос) и принятие из формы в метод POST (POST запрос)
@method_decorator(login_required(), name='dispatch')
class ShowDocumentView(TemplateView):
    documents_form = 'profile_user/documents_form/document.html'
    template_name = 'profile_user/tinymce.html'

    def post(self, request, *args, **kwargs):
        cur_doc = request.POST.get('document')

        document_names = {
            'garanty_doc': 'Акт о гарантии',
            'adoption_doc': 'Акт о принятии',
            'cancell_doc': 'Акт о отказе',
            'complete_doc': 'Акт о выполненных работах'
        }

        name = document_names.get(cur_doc)
        document_object = DocumentInformation.objects.get(user = self.request.user, name = name)
        document_info = DocumentInfoForm(self.request.POST, instance=document_object)

        if document_info.is_valid():
            if document_info.has_changed():

                # Здесь активируется главное сохранение
                document_info.save()
                response = HttpResponse(status=204)
                response['HX-Trigger'] = 'success_save_doc'
                return response
        
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'no_changes_doc' 
            return response
        
        return HttpResponse(status=400)

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
                return render(request, self.documents_form, {'content': content, 'cur_doc': document_selected})
            
        # Если метод получения информации без HTMX, то сначала необходимо загрузить форму (только 1 раз)
        # потом отобразить текст и скрыто передать форму для "фальстарта"
        form = DocumentInfoForm()
        return render(request, self.template_name, {'tiny_mce': form } )
