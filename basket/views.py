from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from basket.basket import Basket
from products.models import Product


def basket_add(request):
    basket = Basket(request)
    if request.POST.get('action') == 'add':
        product_id = int(request.POST.get('product_id'))
        qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        basket.add(product, qty)
        basket_total = basket.get_total_price()
        basketqty = basket.__len__()
        product_subtotal = product.price * qty
        response = JsonResponse({
            'qty': basketqty,
            'subtotal': basket_total,
            'product_subtotal': product_subtotal,
        })

    return response


def basket_page(request):
    return render(request, 'basket/basket.html')


def basket_delete(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('productid')
        basket.delete(product_id=product_id)

        basket_qty = basket.__len__()
        basket_total = basket.get_total_price()
        response = JsonResponse(
            {'qty': basket_qty, 'subtotal': basket_total})
        return response

