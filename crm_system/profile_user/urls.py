from django.urls import path
from profile_user.views import UserProfileView, ShowAdoptionView, ShowCancellView, ShowCompleteView, ServiceSetupView, ShowIssuancetView, WorkersAddView, CreateServiceInfoView, ShowCategoriesView, ShowDocumentView
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    # Выход пользователя из авторизации
    path('logout', LogoutView.as_view(next_page="auth"), name='logout'),
    # Отображение непосредственно ФОРМЫ для ввода данных
    path('make_configuration', ServiceSetupView.as_view(), name='make_config'),
    # А здесь уже СОХРАНЕНИЕ введенной формы 
    path('confirm_conf', CreateServiceInfoView.as_view(), name='confirm_conf'),
    # Отображение формы для ввода данных сотрудников
    path('create_workers', WorkersAddView.as_view(), name='create_workers'),
    # Показ категорий для заказов
    path('categories', ShowCategoriesView.as_view(), name='categories'),
    # Указываю на путь к редактированию документов
    path('documents', ShowDocumentView.as_view(), name='tiny_mce'),
    # Указываю путь к показу и редактированию именно АКТА О ВЫДАЧЕ
    path('document1', ShowIssuancetView.as_view(), name = 'issuance_doc'),
    # Указываю путь к показу и редактированию именно АКТА О ПРИНЯТИИ
    path('document2', ShowAdoptionView.as_view(), name = 'adoption_doc'),
    # Указываю путь к показу и редактированию именно АКТА О ОТКАЗЕ
    path('document3', ShowCancellView.as_view(), name = 'cancell_doc'),
    # Указываю путь к показу и редактированию именно АКТ О ВЫПОЛНЕННЫХ РАБОТАХ
    path('document4', ShowCompleteView.as_view(), name = 'complete_doc'),
]
