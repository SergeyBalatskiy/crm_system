from django import forms
from django.forms import modelformset_factory, BaseModelFormSet
from storage.models import HistoryStorageInfo
from finance.models import FinanceHistoryInfo
from dal_select2.widgets import Select2
from decimal import Decimal

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

class BaseFinanceForm(forms.ModelForm):
    number_in_the_operation = forms.CharField(
        label="Сумма, ₽",
        widget=forms.TextInput(attrs={'class': 'no-spinners', 'autocomplete': 'off'})
    )

    class Meta:
        model=FinanceHistoryInfo
        fields=("product_name", "number_in_the_operation", "supplier", "comment")

    def clean_number_in_the_operation(self):
        value = self.cleaned_data.get('number_in_the_operation')
        if value:
            clean_val = str(value).replace(" ", "").replace("\xa0", "").replace("\u202f", "")
            try:
                return Decimal(clean_val) 
            except Exception:
                raise forms.ValidationError("Введите корректное число.")
        return value
        
CommentCashForm = modelformset_factory(
    FinanceHistoryInfo, fields=("comment",), labels={"comment": "Комментарий"}) # Подставляю комментарий рядом с формой 
# InsertCashForm и в момент сохранения записываю в нее данные из InsertCashForm, а комментарий у меня как раз уже имеется! :3

# Форма для поступления финансов (продажа чего-то)
SellCustomForm = modelformset_factory(FinanceHistoryInfo, form=BaseFinanceForm, formset=DisableUniqueFormSet, fields=("product_name", "number_in_the_operation", "supplier", "comment"), labels={
        "product_name": "Причина поступления",
        "number_in_the_operation": "Сумма, ₽",
        "supplier" : "Поставщик",
        "comment" : "Комментарий",
    })

# Форма для исхода финансов (покупка чего-то)
BuyCustomForm = modelformset_factory(FinanceHistoryInfo, form=BaseFinanceForm, formset=DisableUniqueFormSet, fields=("product_name", "number_in_the_operation", "supplier", "comment"), labels={
        "product_name": "Причина списания",
        "number_in_the_operation": "Сумма, ₽",
        "supplier" : "Поставщик",
        "comment" : "Комментарий",
    })
