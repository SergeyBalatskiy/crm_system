from django import forms
from django.forms import modelformset_factory
from .models import StorageInfo, HistoryStorageInfo
from dal_select2.widgets import Select2


StorageAcceptableForm = modelformset_factory(
    StorageInfo, fields=("name_product", "quantity_at_the_purchase", "supplier", "buy_price", "retail_price", "minimum_items_for_notification"), labels={
        "name_product": "Название товара",
        "quantity_at_the_purchase": "Кол-во на момент закупки",
        "supplier" : "Поставщик",
        "buy_price" : "Стоимость в закупке (шт.)", 
        "retail_price" : "Стоимость в продажу (шт.) - Это просто напоминание для себя за сколько планируют продать", 
        "minimum_items_for_notification" : "Напоминание о маленьком кол-ве (шт.)"
    })

RemovalHistoryForm = modelformset_factory(
    HistoryStorageInfo, fields=("name_product_history", "individual_code_history", "quantity_history", "supplier_history"), labels={
        "name_product_history": "Название товара",
        "individual_code_history": "Код товара",
        "quantity_history" : "Количество",
        "supplier_history" : "Поставщик"
    },
    widgets = {
            'name_product_history': Select2(url='storage-autocomplete', attrs = {
                'data-placeholder' : 'Начните вводить название, код или поставщика...'}
                ), 
            # Эти поля заблокированы от ручного ввода 
            'individual_code_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
            'supplier_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
            
            # Одно поле позволяет менять "данные"
            'quantity_history': forms.NumberInput(attrs={'class': 'form-control', 'value': 1, 'min': 1}),
        })

GarantyHistoryForm = modelformset_factory(
    HistoryStorageInfo, fields=("name_product_history", "individual_code_history", "buy_price_history", "quantity_history", "supplier_history"), labels={
        "name_product_history": "Название товара",
        "individual_code_history": "Код товара",
        "buy_price_history" : "Компенсация (₽)",
        "quantity_history" : "Количество",
        "supplier_history" : "Поставщик",
    }, 
    widgets = {
        'name_product_history': Select2(url='storage-autocomplete', attrs = {
            'data-placeholder' : 'Начните вводить название, код или поставщика...'}
            ), 
        # Эти поля заблокированы от ручного ввода 
        'individual_code_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
        'supplier_history': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
        
        # Два поля которые допускают изменять данные для редактирования полей
        'buy_price_history': forms.NumberInput(attrs={'class': 'form-control','min': 0}),
        'quantity_history': forms.NumberInput(attrs={'class': 'form-control','min': 1}),
    }
)



