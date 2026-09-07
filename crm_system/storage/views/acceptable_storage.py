from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from storage.forms import StorageAcceptableForm
from storage.models import StorageInfo, HistoryStorageInfo
from django.contrib import messages
from django.utils import timezone

# Данный класс отвечает за показ сайта где можно добавить новые поступления на склад
@method_decorator(login_required(), name='dispatch') 
class StorageAcceptableCustomView(TemplateView):

    template_name = 'storage/acceptance-storage.html'

    def post(self, request, *args, **kwargs):

        # Получаю все формсеты, которые есть
        formset = StorageAcceptableForm(request.POST)

        # Валидация форм (пропуск не важных полей) + сохранение важных
        if formset.is_valid():

            # Остановка сохранения 
            instances = formset.save(commit=False)

            # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
            for instance in instances:
                instance.user = request.user
                instance.individual_code = instance.id
                instance.remainder = instance.quantity_at_the_purchase
                instance.save()

                # Создаю обьект (один) в HistoryStorageInfo чтобы можно было отследить, что я добавил!
                HistoryStorageInfo.objects.create(type_of_operation_history = 'Поступление', individual_code_history = instance.individual_code, 
                name_product_history = instance.name_product, quantity_history = instance.quantity_at_the_purchase, 
                buy_price_history = instance.buy_price, supplier_history = instance.supplier, 
                remainder_history = instance.remainder, time_of_operation_history = timezone.now(), time_created_history = instance.created_at, user = request.user)

            messages.success(request, 'Новый товар успешно добавлен на склад!')
            return redirect('main-storage')

        return redirect('acceptance-storage')
        
    def get(self, request, *args, **kwargs):

        # Получаю форму для добавления товара
        formset = StorageAcceptableForm(queryset=StorageInfo.objects.none())
        return render(request, self.template_name, {'form_acceptable' : formset})
                                