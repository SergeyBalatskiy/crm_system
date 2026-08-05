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

y = {'bonus_information' : [
        {'field_key': 'day_of_the_end', 'label': 'Крайний срок', 'type': 'text', 'is_required' : False},
        {'field_key': 'urgently', 'label': 'Срочно', 'type': 'checkbox', 'is_required' : False}
    ]
}


tst = "{'type': 'text', 'label': 'Имя клиента', 'order': 1, 'field_key': 'name', 'is_required': True}"
dic = ast.literal_eval(tst)


jsons = {'client_info': [
            "{'type': 'text', 'label': 'Имя клиента', 'order': 1, 'field_key': 'name', 'is_required': True}"
            ], 
        'device_info': [
            "{'type': 'select', 'label': 'Марка', 'order': 3, 'field_key': 'device_company', 'is_required': False}", 
            "{'type': 'select', 'label': 'Тип устройства', 'order': 2, 'field_key': 'type_of_device', 'is_required': False}"
            ], 
        'bonus_information': [
            "{'type': 'select', 'label': 'Менеджер', 'order': 3, 'field_key': 'manager', 'is_required': False}"
            ]
        }

delete = {'field_key': 'manager', 'label': 'Менеджер', 'type': 'select', 'is_required': False, 'order': 3}

for object in x.get('sections', []):
    if object['id'] == objects_show:
        target_lst = object.get('fields', [])
        target_lst.remove(delete)


forms_to_add = {'client_info': ['name'], 'device_info': ['destroyed', 'device_company'], 'bonus_information': ['urgently']}

crm = {
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
lst12 = []
for category_to_add in forms_to_add:
    for category_data in crm.get(category_to_add):
        if category_data['field_key'] in forms_to_add[category_to_add]:
            for i in range(len(forms_to_add[category_to_add])):
                lst12.append(category_data)
            print(lst12)
    lst12 = []