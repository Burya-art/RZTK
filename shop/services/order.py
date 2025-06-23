from django.shortcuts import get_object_or_404
from shop.models import Basket, Order, OrderItem


# Функція create_order з views.py
def create_order_from_basket(user, city, address, address_ref):
    """
    Створює замовлення з кошика користувача.
    Повертає створений об'єкт Order.
    """
    basket = get_object_or_404(Basket, user=user)
    if not basket.items.exists():
        raise ValueError("Кошик порожній. Додайте товари перед оформленням замовлення.")

    order = Order.objects.create(
        user=user,
        address=f"{city}, {address}",
        address_ref=address_ref
    )

    for item in basket.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity
        )

    basket.items.all().delete()
    return order
