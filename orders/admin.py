from django.contrib import admin
from .models import Order, OrderItem
from orders.models import Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'status', 'created']
    list_filter = ['status', 'created']
    search_fields = ['user__username', 'address']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['liqpay_order_id', 'order', 'amount', 'currency', 'status', 'created']
    list_filter = ['status', 'currency', 'created']
    search_fields = ['liqpay_order_id', 'transaction_id', 'order__id']
    readonly_fields = ['created', 'updated', 'transaction_id']