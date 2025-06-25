from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from basket.models import Basket


def create_order_from_basket(user, city, address, address_ref):
    """
    Створює замовлення з кошика користувача.
    Повертає створений об'єкт Order.
    """
    # Знаходимо кошик користувача
    basket = get_object_or_404(Basket, user=user)
    # Перевіряємо що в кошику є товари
    if not basket.items.exists():
        raise ValueError("Кошик порожній. Додайте товари перед оформленням замовлення.")

    # Створюємо основний об'єкт замовлення
    order = Order.objects.create(
        user=user,
        address=f"{city}, {address}",    # Повна адреса доставки
        address_ref=address_ref          # ID відділення Nova Poshta
    )

    # Копіюємо всі товари з кошика в замовлення
    for item in basket.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,      # Посилання на товар
            price=item.product.price,  # Фіксуємо ціну на момент замовлення
            quantity=item.quantity     # Кількість товару
        )

    # Очищаємо кошик після успішного замовлення
    basket.items.all().delete()
    return order