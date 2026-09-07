from django import forms
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from .models import StorageInfo, HistoryStorageInfo
from tinymce.widgets import TinyMCE


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
    })

GarantyHistoryForm = modelformset_factory(
    HistoryStorageInfo, fields=("name_product_history", "individual_code_history", "buy_price_history", "quantity_history", "supplier_history"), labels={
        "name_product_history": "Название товара",
        "individual_code_history": "Код товара",
        "buy_price_history" : "Закупочная цена (шт.)",
        "quantity_history" : "Количество",
        "supplier_history" : "Поставщик"
    })

