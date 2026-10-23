x = {'order_dict': [{'id': 'client_info', 'name': 'Михаил Фролов', 'email': '-', 'phone': '79999999999', 'address': '-'}, {'id': 'device_info', 'color': 'Синий', 'model': 'SM-2004', 'visual': 'Разьебан пиздец', 'destroyed': 'Разьебали об стену', 'complectation': 'Без ЗУ', 'device_company': 'Samsung', 'type_of_device': 'Телефон'}, {'id': 'bonus_information', 'empty_for_add': '', 'comment_of_order': '-', 'custom-prosto-test-pole': '-', 'custom-forma-obiazatelna-no2': '-'}]} 
m = x.get('order_dict')
for i in m:
    print(i)

test = {'id': 'client_info', 'name': 'Михаил Фролов', 'email': '-', 'phone': '79999999999', 'address': '-'} 
for key, value in test.items():
    if key != 'id':
        print(value)