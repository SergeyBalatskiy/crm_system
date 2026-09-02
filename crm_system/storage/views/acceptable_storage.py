from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.models import DocumentInformation
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.staticfiles import finders


# Данный класс отвечает за показ сайта где можно добавить новые поступления на склад
@method_decorator(login_required(), name='dispatch') 
class StorageAcceptableCustomView(TemplateView):

    template_name = 'profile_user/storage/acceptance-storage.html'

    def post(self, request, *args, **kwargs):

        # cur_doc = request.POST.get('current_document')

        # # Для получения названия документа
        # document_name = {
        #     'garanty_doc': 'Акт о гарантии',
        #     'adoption_doc': 'Акт о принятии',
        #     'cancell_doc': 'Акт о отказе',
        #     'complete_doc': 'Акт о выполненных работах'
        # }
        # data_name = document_name.get(cur_doc)
        # document_data = DocumentInformation.objects.get(user = self.request.user, name = data_name)

        # # Получаю .txt название документа
        # document_name_txt = {
        #     'garanty_doc': 'garanty.txt',
        #     'adoption_doc': 'addoption.txt',
        #     'cancell_doc': 'cancell.txt',
        #     'complete_doc': 'complete.txt'
        # }
        # txt_name = document_name_txt.get(cur_doc)

        # # Ищу "место" где у меня находится мой .txt файл
        # # Когда указывается путь к файлу который находится в статике, необходимо писать путь самого приложения + папку которую нужно найти
        # file_path_txt = finders.find(f'auth_registration/txt/{txt_name}')
        
        # # Открываю, записываю в переменную, внедряю текущий документ в базу данных и сохраняю:
        # with open(file_path_txt, 'r', encoding='utf-8') as file:
        #     clear_document = file.read()
        #     document_data.content = clear_document
        #     document_data.save()

        # # Отдаю контент (Размету документа)
        # content = document_data.content

        # # Название документа на eng
        # document_selected = cur_doc

        # # ОТДАЮ И название, и текст и сообщение
        # response = render(
        #     request, 
        #     self.documents_form, 
        #     {'content': content, 'cur_doc': document_selected}, 
        #     status=200
        # )
        # response['HX-Trigger'] = 'backup_success' 

        # return response
        ...
        
    def get(self, request, *args, **kwargs):
            ...
                        