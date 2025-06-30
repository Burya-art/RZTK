import pytest
from orders.services import create_order_from_basket
from orders.models import Order, OrderItem
from basket.models import BasketItem
from products.models import Product
from decimal import Decimal


@pytest.mark.django_db
class TestOrderServices:

    def test_create_order_from_basket_success(self, user, basket_item):
        """Тест успішного створення замовлення з кошика"""
        # Викликаємо сервіс
        order = create_order_from_basket(
            user=user,
            city="Київ",
            address="вул. Тестова, 1",
            address_ref="ref_123"
        )

        # Перевіряємо створене замовлення
        assert order.user == user
        assert order.address == "Київ, вул. Тестова, 1"
        assert order.address_ref == "ref_123"
        assert order.status == "pending"

        # Перевіряємо що товар скопійований в замовлення
        order_items = OrderItem.objects.filter(order=order)
        assert order_items.count() == 1

        item = order_items.first()
        assert item.product == basket_item.product
        assert item.quantity == basket_item.quantity
        assert item.price == basket_item.product.price

        # Перевіряємо що кошик очищений
        assert not basket_item.basket.items.exists()

    def test_create_order_from_empty_basket(self, user, basket):
        """Тест помилки при створенні замовлення з порожнього кошика"""
        with pytest.raises(ValueError) as exc_info:
            create_order_from_basket(
                user=user,
                city="Київ",
                address="вул. Тестова, 1",
                address_ref="ref_123"
            )

        assert "Кошик порожній" in str(exc_info.value)
        # Перевіряємо що замовлення не створилось
        assert Order.objects.filter(user=user).count() == 0

    @pytest.mark.django_db
    def test_create_order_multiple_items(self, user, basket, product, category, brand):
        """Тест створення замовлення з кількома товарами в кошику"""
        # Створюємо другий продукт
        product2 = Product.objects.create(
            category=category,
            brand=brand,
            name="Другий продукт",
            slug="second-product",
            price=Decimal("500.00"),
            available=True
        )

        # Додаємо товари в кошик
        BasketItem.objects.create(basket=basket, product=product, quantity=2)
        BasketItem.objects.create(basket=basket, product=product2, quantity=1)

        # Створюємо замовлення
        order = create_order_from_basket(
            user=user,
            city="Харків",
            address="вул. Нова, 5",
            address_ref="ref_456"
        )

        # Перевіряємо, що всі товари скопійовані
        order_items = OrderItem.objects.filter(order=order)
        assert order_items.count() == 2

        # Перевіряємо загальну ціну
        total = order.get_total_price()
        expected_total = (product.price * 2) + (product2.price * 1)
        assert total == expected_total
