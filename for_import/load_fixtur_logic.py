import json
from datetime import datetime
from django.core.management import call_command


name_dict = {'products.category': 3, 'products.product': 4, 'products.property': 5,
             'products.propertycategory': 7, 'products.propertyproduct': 6,
             'promotions.promotions': 1, 'promotions.promotiongroup': 2, 'banners.banners': 8,
             'accounts.client': 9, 'shops.shops': 10, 'shops.shopphoto': 11,
             'shops.shopproduct': 12, 'interval': 13, 'basket.clearingbasket': 14}


def my_load_data(file_path):
    priority_data = {i: [] for i in range(1, 16)}
    with open('media/' + file_path) as f:
        for elem in json.load(f):
            if 'model' in elem:
                if elem['model'] in name_dict:
                    priority_data[name_dict[elem['model']]].append(elem)
                else:
                    priority_data[15].append(elem)
            else:
                text_str = f'-|{datetime.now().strftime("%d-%m-%Y %H:%M")}|-Ошибка  ' \
                           f'{elem}: не определена модель' + "\n"
                with open("media/admin_fixtures/errors_file.txt", "a") as file:
                    file.write(text_str)

        for value in priority_data.values():
            if len(value) != 0:
                for fix in value:
                    with open('media/admin_fixtures/data.json', 'w') as outfile:
                        a = list()
                        a.append(fix)
                        json.dump(a, outfile)
                    try:
                        call_command('loaddata', 'media/admin_fixtures/data.json')
                    except Exception as err:
                        text_str = f'-|{datetime.now().strftime("%d-%m-%Y %H:%M")}|-Ошибка  ' \
                                   f'{elem}: {err}' + "\n"
                        with open("media/admin_fixtures/errors_file.txt", "a") as file:
                            # json.dump(text_str, file)
                            file.write(text_str)
