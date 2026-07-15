from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib import messages
from profile_user.models import StatusCategory

# Create your views here.
# Креате вью отвечает за создание нового обьекта на в связке с формой
class RegisterView(CreateView):
    # Само взаимодействие с формой
    form_class = CustomUserCreationForm
    # Какую страницу отображать (это просто с чем мы взаимодействуем)
    template_name = 'auth_registration/auth.html'
    # Что делать в случае 
    success_url = '/profile'

    # Диспатч является функцией аля-Бефор-рекуест
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    # Сохранение дефолтных категорий для заказов (статусов)
    def create_default_categories(self, user):
        default_categories = [
            {"name": "Новый", "color": "#3498db", "category":"new"},
            {"name": "На ремонте", "color": "#ac03f4", "category":"in_process"},
            {"name": "На согласовании", "color": "#ff8c00", "category":"deferred"},
            {"name": "Готов", "color": "#2ecc71", "category":"success"},
            {"name": "Отказ", "color": "#e74c3c", "category":"finished"},
            {"name": "Выдан", "color": "#666666", "category":"finished"},
        ]
        
        for element in default_categories:
            create_category = StatusCategory.objects.create(name=element["name"], color=element["color"], category=element["category"], user=user)
        
        # Возвращаю "ничего" потому что могу себе позволить!
        return None

    # Непосредственно отвечает за валидацию и принятие формы и ее сохранение
    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email  
        user.save() 
        # После сохранения я вызываю функцию которая задает дефолт статусы заказов
        self.create_default_categories(user)
        return login(self.request, user)
    
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth_registration/auth.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    # В случае входа делаю редирект
    def form_valid(self, request):
        # ОЧЕНЬ СОМНЕВАЮСЬ В ЦЕЛЕСООБРАЗНОСТИ ДАННОГО РЕДИРЕКТА
        if request.user.service_info.name_service and request.user.service_info.name_service.address:
            return redirect('profile')
        return redirect('make_config')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(login_form=form,registration_form=CustomUserCreationForm()))

# Темплейт вью отвечает за отображение всех элементов на сайте
class ShowForm(TemplateView):
    # Гоыворим, где нам применять темплейт вью
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
    
