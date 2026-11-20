from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.forms import DocumentInfoForm
from profile_user.models import DocumentInformation


# Показывает акт о принятии
@method_decorator(login_required(), name="dispatch")
class ShowAdoptionView(TemplateView):
    template_name = "profile_user/adoption_doc.html"

    def form_valid(self, document_info):
        # Вношу в переменную обьект из базы данных о принятии
        upd_adoption = DocumentInformation.objects.get(
            user=self.request.user, name="Акт о принятии"
        )
        # Опираясь на форму контент, перезаписываю!
        upd_adoption.content = document_info.cleaned_data["content"]
        # Сохраняю без принудительной остановки так как нужно только перезаписать то, что
        # находится в content
        print(upd_adoption.content)
        upd_adoption.save()

        return redirect("adoption_doc")

    def post(self, request, *args, **kwargs):

        document_info = DocumentInfoForm(
            self.request.POST
        )  # Делать так нужно ОБЯЗАТЕЛЬНО!
        # Проверяю
        if document_info.is_valid():
            # Здесь активируется функция, которая отвечает за главное сохранение
            return self.form_valid(document_info)

        return render(request, self.template_name, {"tiny_mce": document_info})

    def get(self, request, *args, **kwargs):
        document = DocumentInformation.objects.filter(
            name="Акт о принятии", user=self.request.user
        ).first()
        formset = DocumentInfoForm(instance=document)
        return render(request, self.template_name, {"tiny_mce": formset})
