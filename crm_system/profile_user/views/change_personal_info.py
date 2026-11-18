from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.forms import ServiceInfoForm
from profile_user.models import ServiceInfo
from django.contrib import messages
from django.urls import reverse_lazy
from auth_registration.forms import CustomUserCreationForm


# Класс который  отвечает за показ личной информации пользователя и за ее изменение
@method_decorator(login_required(), name="dispatch")
class ChangePersonalInformationView(UpdateView):
    template_name = "profile_user/personal_info.html"
    success_url = reverse_lazy("profile")

    def get(self, request, *args, **kwargs):

        return render(
            request,
            self.template_name,
            context={
                "get_personal_info": CustomUserCreationForm(instance=request.user)
            },
        )

    def post(self, request, *args, **kwargs):

        form = CustomUserCreationForm(
            request.POST, instance=request.user, current_user=request.user
        )
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            super().form_valid(form)
            return redirect("profile")

        return render(
            request,
            self.template_name,
            context={"get_personal_info": form},
        )

    def get_object(self, queryset=None):
        return self.request.user
