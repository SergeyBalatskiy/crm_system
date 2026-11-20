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

# Показывает акт о принятии
@method_decorator(login_required(), name='dispatch')
class ShowAdoptionView(TemplateView):
    template_name = 'profile_user/adoption_doc.html'

    def form_valid(self, document_info):
        # Вношу в переменную обьект из базы данных о принятии
        upd_adoption = DocumentInformation.objects.get(user = self.request.user, name = 'Акт о принятии')
        # Опираясь на форму контент, перезаписываю!
        upd_adoption.content = document_info.cleaned_data['content']
        # Сохраняю без принудительной остановки так как нужно только перезаписать то, что
        # находится в content
        print(upd_adoption.content)
        upd_adoption.save()
                
        return redirect("adoption_doc")


    def post(self, request, *args, **kwargs):

        # ЛИШНИМ НЕ БУДЕТ!
        # import bleach

        # sanitizer = bleach.Sanitizer()
        # cleaned_body = sanitizer.sanitize(form.cleaned_data['body'])
        # post.body = cleaned_body

        # Короче, почему стоит именно писать document_info = DocumentInfoForm(self.request.POST) вместо
        # document_info = self.request.POST.get('context')? ПОТОМУ что все изначально зависит от того, на
        # сколько у нас тесная связь между Frontend и Backend! Если она представляет из себя обычные взаимо-
        # действия (Получи и сохрани), то обязательно применять именно document_info = DocumentInfoForm(self.request.POST), 
        # потому-что основываясь на внесении в переменную форму с полученными данными, я смогу написать потом 
        # if document_info.is_valid(): , а вот если бы я писал document_info = self.request.POST.get('context'), то
        # джанго-функция к такому методу ПОЛУЧЕНИЯ информации - НЕ ПРИМЕНИМА! Да и еще это удобнее!
        # НЕ ЗАБЫВАЮ ПРО document_info.save(commit=False), save_document.name = "Квитанция о приеме", save_document.save() !
        document_info = DocumentInfoForm(self.request.POST) # Делать так нужно ОБЯЗАТЕЛЬНО!
        # Проверяю
        if document_info.is_valid():
            # Здесь активируется функция, которая отвечает за главное сохранение
            return self.form_valid(document_info)

        return render(request, self.template_name, {'tiny_mce': document_info})

    def get(self, request, *args, **kwargs):
        document = DocumentInformation.objects.filter(name='Акт о принятии', user = self.request.user).first()
        formset = DocumentInfoForm(instance=document)
        return render(request, self.template_name, {'tiny_mce': formset})
    