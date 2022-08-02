from basket.models import BasketItem


def basket(request):
    """
    При помощи этого контекст процессора на странице всегда есть инфа о корзине
    """
    if request.user.is_authenticated:
        basket = BasketItem.objects.filter(client=request.user.client)
    else:
        basket = BasketItem.objects.filter(session=request.session.session_key)
    return {'basket':  basket}
