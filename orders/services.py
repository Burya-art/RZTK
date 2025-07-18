from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Payment
from basket.models import Basket
from django.conf import settings
from liqpay3.liqpay import LiqPay
import uuid
import logging
import re

logger = logging.getLogger(__name__)


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
        address=f"{city}, {address}",  # Повна адреса доставки
        address_ref=address_ref  # ID відділення Nova Poshta
    )

    # Копіюємо всі товари з кошика в замовлення
    for item in basket.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,  # Посилання на товар
            price=item.product.price,  # Фіксуємо ціну на момент замовлення
            quantity=item.quantity  # Кількість товару
        )

    # Очищаємо кошик після успішного замовлення
    basket.items.all().delete()
    return order


class LiqPayService:
    """
    Сервіс для роботи з LiqPay API
    """

    def __init__(self):
        self.public_key = settings.LIQPAY_PUBLIC_KEY
        self.private_key = settings.LIQPAY_PRIVATE_KEY
        self.liqpay = LiqPay(
            public_key=self.public_key,
            private_key=self.private_key,
        )

    def create_payment(self, order: Order, success_url, server_url):
        """Створює платіж для замовлення"""

        # Генеруємо унікальний ID для платежу
        payment_id = f"order_{order.id}_{uuid.uuid4().hex[:8]}"

        # Створюємо запис платежу в базі
        payment = Payment.objects.create(
            order=order,
            liqpay_order_id=payment_id,
            amount=order.get_total_price(),
            currency='UAH',
            status='pending'
        )

        logger.info(f"Створено платіж {payment.liqpay_order_id} для замовлення {order.id}")
        return payment

    def get_payment_form_data(self, payment: Payment, success_url, server_url):
        """Генерує дані для форми LiqPay"""
        params = {
            'action': 'pay',
            'amount': float(payment.amount),
            'currency': payment.currency,
            'description': f'Оплата замовлення #{payment.order.id}',
            'order_id': payment.liqpay_order_id,
            'result_url': success_url,
            'server_url': server_url,
            'language': 'uk'
        }

        # Використовуємо cnb_form і витягуємо дані
        full_form = self.liqpay.cnb_form(params)

        # Витягуємо data та signature з HTML форми
        data_match = re.search(r'name="data" value="([^"]+)"', full_form)
        signature_match = re.search(r'name="signature" value="([^"]+)"', full_form)

        data_encoded = data_match.group(1) if data_match else None
        signature = signature_match.group(1) if signature_match else None

        # Повертаємо дані для кастомної форми
        form_data = {
            'data': data_encoded,
            'signature': signature,
            'action_url': 'https://www.liqpay.ua/api/3/checkout'
        }
        logger.info(f"Згенеровано форму для платежу {payment.liqpay_order_id}")
        return form_data

    def process_callback(self, data, signature):
        """Обробляє callback від LiqPay"""
        try:
            # Перевіряємо підпис
            if not self.liqpay.str_to_sign(data) == signature:
                logger.error("Невірний підпис callback від LiqPay")
                return {'status': 'error', "message": 'Invalid signature'}

            # Декодуємо дані
            callback_data = self.liqpay.decode_data_from_str(data)
            order_id = callback_data.get('order_id')
            status = callback_data.get('status')
            transaction_id = callback_data.get('transaction_id')

            logger.info(f"Отримуємо callback для платежу {order_id}: статус {status}")

            # Знаходимо платіж
            try:
                payment = Payment.objects.get(liqpay_order_id=order_id)
            except Payment.DoesNotExist:
                logger.error(f"Платіж {order_id} не знайдено")
                return {'status': 'error', 'message': 'Payment not found'}

            # Оновлюємо статус платежу
            payment.transaction_id = transaction_id

            if status == 'success':
                payment.status = 'success'
                payment.order.status = 'pending'
                payment.order.save()

            elif status == 'failure':
                payment.status = 'failure'

            elif status == 'sandbox':
                payment.status = 'sandbox'
                # У sandbox режимі вважаємо оплату успішною
                payment.order.status = 'pending'
                payment.order.save()

            payment.save()

            logger.info(f"Оновлено статус платежу {order_id} на {payment.status}")

            return {
                'status': 'success',
                'payment_id': payment.id,
                'payment_status': payment.status,
                'order_id': payment.order.id
            }

        except Exception as e:
            logger.error(f"Помилка при обробці callback: {str(e)}")
            return {'status': 'error', 'message': str(e)}
