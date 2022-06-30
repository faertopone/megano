from decimal import Decimal
from products.models import Product


class Basket:
    """
    Класс корзины
    """

    def __init__(self, request):
        self.session = request.session
        basket = self.session.get('skey')
        if 'skey' not in request.session:
            basket = self.session['skey'] = {}
        self.basket = basket

    def add(self, product, qty: int):
        """
        Добавление товара в корзину и обновление данных сессии
        """
        product_id = str(product.id)
        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        else:
            self.basket[product_id] = {'price': str(product.price), 'qty': qty}
        self.session.modified = True

    def __len__(self):
        """
        Для исользования length в шаблоне
        """
        return sum(item['qty'] for item in self.basket.values())

    def __iter__(self):
        """
        Возможность итерирования по классу
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item

    def get_total_price(self) -> int:
        """
        Стоимость корзины
        """
        return sum(Decimal(item['price']) * item['qty'] for item in self.basket.values())

    def delete(self, product_id: str):
        """
        Удалить товар из корзины
        """

        if product_id in self.basket:
            del self.basket[product_id]
            self.session.modified = True