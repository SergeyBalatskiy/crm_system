from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from finance.models import CashAccount
from django.shortcuts import render
from django.db.models import Q, TextField, F
from django.views import View
from django.db.models.functions import Cast
from datetime import timedelta
from datetime import datetime

# Данный класс отвечает за обычный показ баланса сервисного центра
@method_decorator(login_required(), name='dispatch') 
class MainCashView(View):

    def get(self, request, *args, **kwargs):

        get_main_balance, created = CashAccount.objects.get_or_create(user=request.user)
        
        return render(request, 'finance/main_balance.html', {'cash': get_main_balance})
        
        