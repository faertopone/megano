import json
from shops.models import Shops, ShopProduct, ShopPhoto, ShopUser
from products.models import Product, PropertyCategory, PropertyProduct, ProductPhoto, Property
from datetime import datetime
from django.core.management import call_command


name_dict = {'products.category': 3, 'products.product': 4, 'products.property': 5, 'products.propertycategory': 7, 'products.propertyproduct': 6,
             'promotions.promotions': 1, 'promotions.promotiongroup': 2, 'banners.banners': 8, 'accounts.client': 9, 'shops.shops': 10, 'shops.shopphoto': 11,
             'shops.shopproduct': 12, 'interval': 13, 'basket.clearingbasket': 14}


# def for_json_in_db(file_path: str):
#     model_dict = {
#         'shops.shops': Shops,
#         'shops.shopproduct': ShopProduct,
#         'shops.shopphoto': ShopPhoto,
#         'shops.shopuser': ShopUser,
#         'products.product': Product,
#         'products.propertycategory': PropertyCategory,
#         'products.propertyproduct': PropertyProduct,
#         'products.productphoto': ProductPhoto,
#         'products.property': Property
#     }
#     key_list = ['rating', 'house_number', 'amount']
#     with open('media/' + file_path) as f:
#         new_data = json.load(f)
#
#         for i in model_dict:
#
#             if new_data[0]['model'] == i:
#                 for j in new_data:
#                     if 'pk' in j:
#                         print('---pk: ', j['pk'])
#                     obj_for_model = {}
#                     for key, value in j['fields'].items():
#                         if (isinstance(value, set)
#                                 or isinstance(value, list)
#                                 or isinstance(value, dict)
#                                 or key == "flag_limit"
#                                 or key == "tag"):
#                             pass
#                         elif isinstance(value, int) and key not in key_list:
#                             obj_for_model[key + '_id'] = value
#                         else:
#                             obj_for_model[key] = value
#                     print('***************', obj_for_model)
#                     try:
#                         model_dict[i].objects.get_or_create(**obj_for_model)
#                         # call_command('loaddata', obj_for_model)
#                     except Exception as err:
#                         text_str = f'-----{datetime.now().strftime("%d-%m-%Y %H:%M")}------Ошибка  ' \
#                                    f'{i}--{obj_for_model}: {err}' + "\n"
#                         with open("media/admin_fixtures/errors_file.txt", "a") as file:
#                             file.write(text_str)
#                         pass


def my_load_data(file_path):
    priority_data = {i: [] for i in range(1, 16)}
    with open('media/' + file_path) as f:
        for elem in json.load(f):
            if elem['model'] in name_dict:
                priority_data[name_dict[elem['model']]].append(elem)
            else:
                priority_data[15].append(elem)

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

