from django import forms
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from .models import StorageInfo
from tinymce.widgets import TinyMCE


StorageAcceptableForm = modelformset_factory(
    StorageInfo, fields=("name_product", "quantity_at_the_purchase", "supplier", "buy_price", "retail_price", "minimum_items_for_notification"), labels={
        "name_product": "Название товара",
        "quantity_at_the_purchase": "Кол-во на момент закупки",
        "supplier" : "Поставщик",
        "buy_price" : "Стоимость в закупке (шт.)", 
        "retail_price" : "Стоимость в продаж", 
        "minimum_items_for_notification" : "Напоминание о маленьком кол-ве (шт.)"
    })

