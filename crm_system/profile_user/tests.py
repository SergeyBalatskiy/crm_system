from django.test import TestCase
import ast

# Create your tests here.
x = {'sections': [{
         'id':'client_info', 
         'title' : 'Клиент',
         'order' : 1,
         'fields' : [{
             'field_key' : 'name',
             'label' : 'Имя клиента',
             'type' : 'text',
             'is_required' : True,
             'order' : 1
         },
         {
            'field_key' : 'phone',
             'label' : 'Телефон',
             'type' : 'phone',
             'is_required' : True,
             'order' : 2
         },
         {
             'field_key' : 'telegram',
             'label' : 'Телеграм',
             'type' : 'text',
             'is_required' : False,
             'order' : 3
         }
        ]
    },
    {
        'id':'device_info', 
        'title' : 'Устройство и неисправности',
        'order' : 2,
        'fields' : [{
            'field_key' : 'serial_number',
            'label' : 'Серийный номер',
            'type' : 'text',
            'is_required' : False,
            'order' : 1
         },
         {
            'field_key' : 'type_of_device',
            'label' : 'Тип устройства',
            'type' : 'select',
            'is_required' : False,
            'order' : 2
         },
         {
            'field_key' : 'device_company',
            'label' : 'Марка',
            'type' : 'select',
            'is_required' : False,
            'order' : 3
         },
         {
            'field_key' : 'color',
            'label' : 'Цвет',
            'type' : 'select',
            'is_required' : False,
            'order' : 4
         }
        ]
    },
    {
        'id':'bonus_information', 
        'title' : 'Дополнительная информация',
        'order' : 3,
        'fields' : [{
            'field_key' : 'target_price',
            'label' : 'Ориентировочная цена',
            'type' : 'number',
            'is_required' : False,
            'order' : 1
         },
         {
            'field_key' : 'master',
            'label' : 'Мастер',
            'type' : 'select',
            'is_required' : False,
            'order' : 2
         },
         {
            'field_key' : 'manager',
            'label' : 'Менеджер',
            'type' : 'select',
            'is_required' : False,
            'order' : 3
         },
         {
            'field_key' : 'comment_of_order',
            'label' : 'Комментарий приемщика',
            'type' : 'textarea',
            'is_required' : False,
            'order' : 4
         }
        ]
    }
    ]}


ALL_CRM_FIELDS = {
    'client_info': [
        {'field_key': 'name', 'label': 'Имя клиента', 'type': 'text'},  
        {'field_key': 'phone', 'label': 'Телефон', 'type': 'phone'},    
        {'field_key': 'telegram', 'label': 'Телеграм', 'type': 'text'}, 
        {'field_key': 'address', 'label': 'Адрес клиента', 'type': 'text'},
        {'field_key': 'ad_source', 'label': 'Рекламный источник', 'type': 'select'},
        {'field_key': 'email', 'label': 'Email', 'type': 'email'},
    ],
    'device_info': [
        {'field_key': 'serial_number', 'label': 'Серийный номер / IMEI', 'type': 'text'},
        {'field_key': 'type_of_device', 'label': 'Тип устройства', 'type': 'select'},
        {'field_key': 'device_company', 'label': 'Марка', 'type': 'select'},
        {'field_key': 'model', 'label': 'Модель', 'type': 'text'},
        {'field_key': 'color', 'label': 'Цвет', 'type': 'text'},
        {'field_key': 'visual', 'label': 'Внешний вид', 'type': 'select'},
        {'field_key': 'destroyed', 'label': 'Неисправность', 'type': 'text'},
        {'field_key': 'complectation', 'label': 'Комплектация', 'type': 'select'},

    ],
    'bonus_information' : [
        {'field_key': 'comment_of_order', 'label': 'Комментарий приемщика', 'type': 'textarea'},
        {'field_key': 'master', 'label': 'Мастер', 'type': 'select'},
        {'field_key': 'manager', 'label': 'Менеджер', 'type': 'select'},
        {'field_key': 'prepay', 'label': 'Предоплата', 'type': 'checkbox'},
        {'field_key': 'day_of_the_end', 'label': 'Крайний срок', 'type': 'text'},
        {'field_key': 'target_price', 'label': 'Ориентировочная цена', 'type': 'number'},
        {'field_key': 'urgently', 'label': 'Срочно', 'type': 'checkbox'},
    ]
}

objects_show = 'bonus_information'

lst_current = []


not_lst = []
for obj_info in x.get('sections', []):
    ...
    # print(obj_info['id'])

s = x.get('sections')

print(s[0])