from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from finance.models import FinanceHistoryInfo
from django.http import HttpResponse
from django.shortcuts import render
from finance.forms import SellCustomForm, BuyCustomForm
from django.contrib.staticfiles import finders

# Данный класс отвечает за обычный показ выбора финансовой транзакции для ОСТАЛЬНОЕ
@method_decorator(login_required(), name='dispatch') 
class ShowOthersCustomView(TemplateView):

    sell_other = 'finance/sell_other/sell_other.html'
    template_name = 'finance/buy_sell_other.html'
    buy_other = 'finance/buy_other/buy_other.html'

    def get(self, request, *args, **kwargs):

        if request.headers.get('HX-Request') == 'true':
            type_of_other_selected = request.GET.get('type_of_other_selected')

            if type_of_other_selected == 'sell_other':
                # Получаю форму для "остальной" транзакции на поступление
                formset = SellCustomForm(queryset=FinanceHistoryInfo.objects.none())
                return render(request, self.sell_other, {'form_sell_other' : formset})

            # Получаю форму для "остальной" транзакции на покупку (исход)
            formset = BuyCustomForm(queryset=FinanceHistoryInfo.objects.none())
            return render(request, self.buy_other, {'form_buy_other' : formset})

        return render(request, self.template_name)
