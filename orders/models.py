from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=250)
    address_ref = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Очікує обробки'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ], default='pending')

    class Meta:
        db_table = 'orders'
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created']  # Сортуємо за датою створення (новіші перші)

    def __str__(self):
        return f'Замовлення {self.id} від {self.user.username}'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Елемент замовлення'
        verbose_name_plural = 'Елементи замовлення'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Замовлення {self.order.id})'

    def get_total_price(self):
        return self.quantity * self.price
