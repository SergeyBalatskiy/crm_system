from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.forms import DocumentInfoForm
from profile_user.models import DocumentInformation


# Показывает акт о выполненных работах
@method_decorator(login_required(), name="dispatch")
class ShowCompleteView(TemplateView):
    template_name = "profile_user/complete_doc.html"

    def form_valid(self, document_info):
        upd_complete = DocumentInformation.objects.get(
            user=self.request.user, name="Акт о выполненных работах"
        )
        upd_complete.content = document_info.cleaned_data["content"]

        upd_complete.save()
        print(upd_complete.content)

        return redirect("complete_doc")

    def post(self, request, *args, **kwargs):

        document_info = DocumentInfoForm(
            self.request.POST
        )  # Делать так нужно ОБЯЗАТЕЛЬНО!
        # Проверяю
        if document_info.is_valid():
            # Здесь активируется функция, которая отвечает за главное сохранение
            return self.form_valid(document_info)

        return render(request, self.template, {"tiny_mce": document_info})

    def get(self, request, *args, **kwargs):
        document = DocumentInformation.objects.filter(
            name="Акт о выполненных работах", user=self.request.user
        ).first()
        print(document)
        formset = DocumentInfoForm(instance=document)
        return render(request, self.template_name, {"tiny_mce": formset})
