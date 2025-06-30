import pytest
from orders.models import Order, OrderItem
from decimal import Decimal


@pytest.mark.django_db
class TestOrderModel:
    def test_order_creation(self, order):
        """Тест створення замовлення"""
        assert order.user.username == "testuser"
        assert order.address == "Київ, вул. Тестова, 1"
        assert order.address_ref == "test_ref_123"
        assert order.status == "pending"
        assert order.created is not None
        assert order.updated is not None

    def test_order_str_method(self, order):
        """Тест методу __str__ замовлення"""
        expected = f'Замовлення {order.id} від {order.user.username}'
        assert str(order) == expected

    def test_order_db_table(self):
        """Тест назви таблиці замовлень"""
        assert Order._meta.db_table == 'orders'

    def test_order_default_status(self, user):
        """Тест статусу замовлення за замовчуванням"""
        order = Order.objects.create(
            user=user,
            address="Тестова адреса"
        )
        assert order.status == "pending"

    def test_order_get_total_price_empty(self, order):
        """Тест розрахунку загальної ціни для порожнього замовлення"""
        assert order.get_total_price() == 0


@pytest.mark.django_db
class TestOrderItemModel:

    def test_order_item_creation(self, order_item):
        """Тест створення товару в замовленні"""
        assert order_item.product.name == "Тестовий продукт"
        assert order_item.price == Decimal("1000.00")
        assert order_item.quantity == 1
        assert order_item.order.user.username == "testuser"

    def test_order_item_str_method(self, order_item):
        """Тест методу __str__ товару в замовленні"""
        expected = f'{order_item.quantity} x {order_item.product.name} (Замовлення {order_item.order.id})'
        assert str(order_item) == expected

    def test_order_item_db_table(self):
        """Тест назви таблиці товарів в замовленні"""
        assert OrderItem._meta.db_table == 'order_items'

    def test_order_item_get_total_price(self, order_item):
        """Тест розрахунку загальної ціни товару"""
        expected_price = order_item.quantity * order_item.price
        assert order_item.get_total_price() == expected_price
        assert order_item.get_total_price() == Decimal("1000.00")

    def test_order_total_price_with_items(self, order, product):
        """Тест розрахунку загальної ціни замовлення з товарами"""
        # Додаємо два товари до замовлення
        OrderItem.objects.create(
            order=order,
            product=product,
            price=Decimal("500.00"),
            quantity=2
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            price=Decimal("300.00"),
            quantity=1
        )

        # Загальна ціна: (500 * 2) + (300 * 1) = 1300
        assert order.get_total_price() == Decimal("1300.00")
