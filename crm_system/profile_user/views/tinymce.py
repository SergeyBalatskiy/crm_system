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

    def form_valid(self, document_info, name):
        upd_doc = DocumentInformation.objects.get(user = self.request.user, name = name)
        upd_doc.content = document_info.cleaned_data["content"]
        upd_doc.save()
        return None

    def post(self, request, *args, **kwargs):
        cur_doc = request.POST.get('name')

        if cur_doc == 'garanty_doc':
            document_info = DocumentInfoForm(self.request.POST) # Делать так нужно ОБЯЗАТЕЛЬНО!
            # Проверяю
            if document_info.is_valid():
                name = 'Акт о гарантии'
                # Здесь активируется функция, которая отвечает за главное сохранение
                return self.form_valid(document_info, name)

        if cur_doc == 'adoption_doc':
            document_info = DocumentInfoForm(self.request.POST) # Делать так нужно ОБЯЗАТЕЛЬНО!
            # Проверяю
            if document_info.is_valid():
                name = 'Акт о принятии'
                # Здесь активируется функция, которая отвечает за главное сохранение
                return self.form_valid(document_info, name)

        if cur_doc == 'cancell_doc':
            document_info = DocumentInfoForm(self.request.POST) # Делать так нужно ОБЯЗАТЕЛЬНО!
            # Проверяю
            if document_info.is_valid():
                name = 'Акт о отказе'
                # Здесь активируется функция, которая отвечает за главное сохранение
                return self.form_valid(document_info, name)

        if cur_doc == 'complete_doc':
            document_info = DocumentInfoForm(self.request.POST)
            # Проверяю
            if document_info.is_valid():
                # Здесь активируется функция, которая отвечает за главное сохранение
                name = 'Акт о выполненных работах'
                return self.form_valid(document_info, name)

    # Передаю в сайт методом GET форму самого tinymce
    def get(self, request, *args, **kwargs):
        
        if request.headers.get('HX-Request') == 'true':
            document_selected = request.GET.get('name')

            if document_selected == 'garanty_doc':
                document = DocumentInformation.objects.filter(name='Акт о гарантии', user = self.request.user).first()
                formset = DocumentInfoForm(instance=document)
                button_content = '<button type="submit">Сохранить документ</button>'
                return render(request, self.template_name, {'tiny_mce': formset, 'button': button_content, 'cur_doc' : 'garanty_doc'})

            if document_selected == 'adoption_doc':
                document = DocumentInformation.objects.filter(name='Акт о принятии', user = self.request.user).first()
                formset = DocumentInfoForm(instance=document)
                button_content = '<button type="submit">Сохранить документ</button>'
                return render(request, self.template_name, {'tiny_mce': formset, 'button': button_content, 'cur_doc' : 'adoption_doc'})

            if document_selected == 'cancell_doc':
                document = DocumentInformation.objects.filter(name='Акт о отказе', user = self.request.user).first()
                formset = DocumentInfoForm(instance=document)
                button_content = '<button type="submit">Сохранить документ</button>'
                return render(request, self.template_name, {'tiny_mce': formset, 'button': button_content, 'cur_doc' : 'cancell_doc'})
    
            if document_selected == 'complete_doc':
                document = DocumentInformation.objects.filter(name='Акт о выполненных работах', user = self.request.user).first()
                formset = DocumentInfoForm(instance=document)
                button_content = '<button type="submit">Сохранить документ</button>'
                return render(request, self.template_name, {'tiny_mce': formset, 'button': button_content, 'cur_doc' : 'complete_doc'})
        
        else:
            html_fragment = "Пока что вы не выбрали ни одну форму"
            return render(request, self.template_name, {'message': html_fragment} )

