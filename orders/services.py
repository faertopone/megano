from django.http import HttpRequest
from accounts.models import Client


def initial_order_form(request: HttpRequest) -> dict:
    """
    Функция инициализирует начальные значения Профиля
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)
    city = ''
    address = ''
    if client.city:
        city = client.city
    if client.street:
        address = 'Улица ' + client.street + ', дом №' + client.house_number + ', номер квартиры№' + client.apartment_number
    initial_client = {
        'phone': client.phone,
        'patronymic': client.patronymic,
        'first_name': client.user.first_name,
        'last_name': client.user.last_name,
        'email': client.user.email,
        'city': city,
        'address': address
    }
    return initial_client