from django.shortcuts import redirect
from auth_registration.forms import CustomUserCreationForm, LoginForm
from django.views.generic import TemplateView



# Темплейт вью отвечает за отображение всех элементов на сайте
class ShowForm(TemplateView):
    # Говорим, где нам применять темплейт вью
    template_name = 'auth_registration/auth.html'

    def dispatch(self, request, *args, **kwargs):
        # Тут редирект в случае того что пользователь авторизирован
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)
    
    # Функция которая отвечает за отображение даннных в самом шаблоне сайта .html
    def get_context_data(self, **kwargs):
        # Это обязательно!!!
        context = super().get_context_data(**kwargs)
        # Передаем формы как регистрации так и логирования
        context['registration_form'] = CustomUserCreationForm()
        context['login_form'] = LoginForm()
        # Обязательно передается в виде словаря
        return context
    
