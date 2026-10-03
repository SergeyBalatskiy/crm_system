from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from storage.models import StorageInfo
from django.shortcuts import render
from django.db.models import Q, TextField, F
from django.views import View
from django.db.models.functions import Cast
from datetime import timedelta
from datetime import datetime
from services.models import ServicesInfo

class ShowAndCreateServicesWork(View):
    def get(self, request, *args, **kwargs):
        # Получаю все созданные ранее услуги в БД:
        get_services = ServicesInfo.objects.filter(user=request.user)
        context = {'service_works' : get_services}
        return render(request, 'services/services_main.html', context)
                

    

    def post(self, request, *args, **kwargs):
        ...