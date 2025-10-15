from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        self.promo_code = self.session.get('promo_code')

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_item_total_price(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            price = float(self.cart[product_id]['price'])
            quantity = self.cart[product_id]['quantity']
            return price * quantity
        return 0

    def get_total_price(self):
        total = 0
        for item in self.cart.values():
            price = float(item['price'])
            quantity = item['quantity']
            total += price * quantity
        return round(total, 2)

    def apply_promo_code(self, code):
     from .models import PromoCode
    
     print(f"=== ПОИСК ПРОМОКОДА ===")
     print(f"Ищем: '{code}'")
     print(f"Преобразовано в верхний регистр: '{code.upper()}'")
    
     try:
        # Сначала попробуем найти как есть
        promo = PromoCode.objects.get(code=code.upper())
        print(f"✅ Найден промокод: '{promo.code}'")
        
        # Проверим все условия
        from django.utils import timezone
        now = timezone.now()
        print(f"Активен: {promo.active}")
        print(f"Использований: {promo.used_count}/{promo.max_usage}")
        print(f"Действует с: {promo.valid_from}")
        print(f"Действует до: {promo.valid_to}")
        print(f"Текущее время: {now}")
        print(f"В пределах дат: {promo.valid_from <= now <= promo.valid_to}")
        
        self.session['promo_code'] = {
            'code': promo.code,
            'discount': promo.discount
        }
        self.save()
        return True, promo
        
     except PromoCode.DoesNotExist:
        print("❌ Промокод не найден!")
        # Выведем все промокоды для отладки
        all_promos = PromoCode.objects.all()
        print("Все промокоды в базе:")
        for p in all_promos:
            print(f"  - '{p.code}'")
        return False, "Промокод не найден"
    
    def remove_promo_code(self):
        if 'promo_code' in self.session:
            del self.session['promo_code']
            self.save()

    def get_discount(self):
    # Проверяем, есть ли промокод в сессии
     if 'promo_code' in self.session:
        discount = self.session['promo_code'].get('discount', 0)
        print(f"🎯 Текущая скидка из сессии: {discount}%")
        return discount
     else:
        print("🎯 Промокод не найден в сессии")
        return 0

    def get_total_with_discount(self):
     total = self.get_total_price()
     discount = self.get_discount()
     print(f"🔧 Расчет скидки: total={total}, discount={discount}%")
    
     if discount:
        discounted_total = total * (100 - discount) / 100
        print(f"🔧 Итог со скидкой: {discounted_total} ₽")
        return round(discounted_total, 2)
     return total

    def __iter__(self):
     from catalog.models import Product
     product_ids = self.cart.keys()
     products = Product.objects.filter(id__in=product_ids)
     cart = self.cart.copy()
    
     for product in products:
        cart[str(product.id)]['product'] = product
        cart[str(product.id)]['product_id'] = product.id  # 👈 добавляем id
    
     for item in cart.values():
        item['total_price'] = float(item['price']) * item['quantity']
        yield item
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session['cart']
        self.save()