from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from basket.models import BasketItem
from products.models import Product
from promotions.services import PromotionService
from shops.models import Shops, ShopProduct


promotion_service = PromotionService()


def basket_add(request):
    if request.POST.get('action') == 'add':
        product_id = int(request.POST.get('product_id'))
        shop_product_id = int(request.POST.get('shop_product_id', 0))
        if not shop_product_id:
            shop_product = ShopProduct.objects.filter(product=product_id).first()
        else:
            shop_product = ShopProduct.objects.get(id=shop_product_id)
        shop = Shops.objects.get(shop_product=shop_product)
        qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)

        prices = shop_product.get_prices_with_promotion(promotion_service)
        basket_item, _ = BasketItem.objects.my_update_or_create(
            request=request,
            product=product,
            defaults={
                'qty': qty, 'price': prices.new_price if prices.new_price else prices.old_price,
                'old_price': prices.old_price if prices.new_price else 0,
                'shop': shop, 'shop_product': shop_product
            }
        )

        client_basket = BasketItem.objects.smart_filter(request=request)
        response = JsonResponse({
            'qty': client_basket.total_count,
            'subtotal': client_basket.total_price,
            'discount_subtotal': client_basket.total_old_price,
            'product_subtotal': basket_item.total_price,
            'item_qty': basket_item.qty,
            'product_discount_subtotal': basket_item.total_old_price if basket_item.total_old_price else None,
        })
    if request.POST.get('action') == 'change_shop':
        shop_product_id = int(request.POST.get('shop_product_id'))
        shop_product = ShopProduct.objects.get(id=shop_product_id)
        client_basket = BasketItem.objects.smart_filter(request=request)

        prices = shop_product.get_prices_with_promotion(promotion_service)
        basket_item, _ = client_basket.update_or_create(
            product=shop_product.product, defaults={
                'shop': shop_product.shop,
                'price': prices.new_price if prices.new_price else prices.old_price,
                'old_price': prices.old_price if prices.new_price else 0,
                'shop_product': shop_product
            })
        response = JsonResponse({
            'qty': client_basket.total_count,
            'subtotal': client_basket.total_price,
            'discount_subtotal': client_basket.total_old_price,
            'product_subtotal': basket_item.total_price,
            'product_discount_subtotal': basket_item.total_old_price if basket_item.total_old_price else None,
            'item_qty': basket_item.qty,
            'product_id': shop_product.product.id
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
            'qty': client_basket.total_count,
            'subtotal': client_basket.total_price,
            'discount_subtotal': client_basket.total_old_price,
        })
        return response
