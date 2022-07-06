from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from basket.models import BasketItem
from products.models import Product


def basket_add(request):
    if request.POST.get('action') == 'add':
        product_id = int(request.POST.get('product_id'))
        qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        basket_item, _ = BasketItem.objects.my_update_or_create(
            request=request,
            product=product,
            defaults={'qty': qty, 'price': product.price}
        )
        client_basket = BasketItem.objects.smart_filter(request=request)
        response = JsonResponse({
            'qty': client_basket.total_count(),
            'subtotal': client_basket.get_total_price(),
            'product_subtotal': basket_item.total_price,
            'item_qty': basket_item.qty
        })
    return response


def basket_page(request):
    return render(request, 'basket/basket.html')


def basket_delete(request):
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('productid')
        basket_item = BasketItem.objects.get_item(request=request, product=product_id)
        basket_item.delete()
        client_basket = BasketItem.objects.smart_filter(request=request)
        response = JsonResponse({
            'qty': client_basket.total_count(),
            'subtotal': client_basket.get_total_price()
        })
        return response
