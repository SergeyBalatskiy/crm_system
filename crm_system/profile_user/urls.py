from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    # Выход пользователя из авторизации
    path('logout', LogoutView.as_view(next_page="auth"), name='logout'),
    # Отображение сайта для настройки данных сервиса
    path('service_information', ServiceInfoView.as_view(), name = 'service_info'), # Осталось доделать визуал названия сервиса и его адрес А ПОТОМ переходить к складу + УСЛУГИ
    # Отображение формы для ввода данных сотрудников
    path('workers', WorkersAddView.as_view(), name='workers'),
    # Показ категорий для заказов
    path('categories', ShowCategoriesView.as_view(), name='categories'),
    # Указываю на путь к редактированию документов
    path('documents', ShowDocumentView.as_view(), name='tiny_mce'),
    # Указываю на путь к восстановлению документа по умолчанию
    path('backup_default_doc', BackupDocumentView.as_view(), name='backup_default_doc'),
    # Указываю на путь к редактированию форм для заказа
    path('form-editor', FormsForOrdersEdit.as_view(), name='form-editor'),
    # Указываю на путь, где лежит центральное окно с возможностью корректировки каждой формы индивидуально
    path('get-individual-field-modal', EditIndividualCenterForm.as_view(), name='get-individual-field-modal'),
    # Указываю на путь, чтобы можно было СОЗДАТЬ новую форму внутри определенной категории
    path('get-create-new-form', CreateNewFormInCategory.as_view(), name='create-new-form'),
    # Указываю на путь, чтобы можно было УДАЛИТЬ кастомную форму
    path('delete-custom-form', DeleteCustomForm.as_view(), name='delete-custom-form'),
    
]
