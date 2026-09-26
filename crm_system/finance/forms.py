from django import forms
from django.forms import modelformset_factory, BaseModelFormSet
from storage.models import HistoryStorageInfo
from finance.models import FinanceHistoryInfo
from dal_select2.widgets import Select2

# Класс для отключения обязательной уникальности
class DisableUniqueFormSet(BaseModelFormSet):
    def validate_unique(self):
        pass

InsertCashForm = modelformset_factory(
    HistoryStorageInfo, formset=DisableUniqueFormSet, fields=("name_product_history", "individual_code_history", "buy_price_history", "quantity_history", "supplier_history"), labels={
        "name_product_history": "Название товара",
        "individual_code_history": "Код товара",
        "buy_price_history" : "Цена продажи (₽)",
        "quantity_history" : "Количество",
        "supplier_history" : "Поставщик",
    }, 
    widgets = {
        'name_product_history': Select2(url='finance-autocomplete', attrs = {
            'data-placeholder' : 'Начните вводить название, код или поставщика...'}
            ), 
        # Эти поля заблокированы от ручного ввода 
        'individual_code_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
        'supplier_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
        
        # Заменено на TextInput для корректной работы форматирования пробелов в JS
        'buy_price_history': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'placeholder': '0'}),
        'quantity_history': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'placeholder': '1'}),
    }
)

CommentCashForm = modelformset_factory(
    FinanceHistoryInfo, fields=("comment",), labels={"comment": "Комментарий"})



