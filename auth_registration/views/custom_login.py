from django.shortcuts import redirect
from auth_registration.forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "auth_registration/auth.html"

    # Очень важное уточнение ЗДЕСЬ! ТАК как я использую LoginView, то
    # важно его писать именно обращаясь к классу с унаследованием функции супер
    # form_valid! Так как если этого не делать, то из за того, что ты напишешь так:
    #
    #    def form_valid(self, form):
    #    return redirect('profile')
    #
    # Получится так, что ты в текущей функции ПЕРЕЗАПИШЕШЬ ВСЮ ТУ МЕХАНИКУ, КОТОРАЯ
    # ПО дефолту реализована была уже!

    def form_valid(self, form):
        # Обязательно сначала "наследуюсь от супер функции form_valid"
        super().form_valid(form)
        return redirect("profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("profile")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "login_form" not in context:
            context["login_form"] = self.get_form()
        if "registration_form" not in context:
            context["registration_form"] = CustomUserCreationForm()

        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(login_form=form))
