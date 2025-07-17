from inspect import signature

from django.contrib.messages.api import success
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Order, Payment
from .services import create_order_from_basket, LiqPayService
from products.models import Category, Brand
from shop.forms import OrderForm
from nova_poshta.services import NovaPoshtaService
from rztk_project.settings import NOVA_POSHTA_API_KEY
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse

logger = logging.getLogger(__name__)

# Инициализация NovaPoshtaService
nova_poshta_service = NovaPoshtaService(NOVA_POSHTA_API_KEY)
logger.debug(f"NOVA_POSHTA_API_KEY: {NOVA_POSHTA_API_KEY}")


@login_required
def create_order(request):
    """Створює нове замовлення на основі товарів з кошика"""
    if request.method == 'POST':
        # Валідуємо дані з форми замовлення
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                # Створюємо замовлення через сервіс із даними доставки
                order = create_order_from_basket(
                    user=request.user,
                    city=form.cleaned_data['city'],  # Місто доставки
                    address=form.cleaned_data['address'],  # Адреса відділення
                    address_ref=form.cleaned_data['address_ref']  # ID відділення Нової Пошти
                )
                messages.success(request, f'Замовлення #{order.id} успішно створено!')
                # Після успішного замовлення перенаправляємо на сторінку оплати
                return redirect('orders:payment_form', order_id=order.id)
            except ValueError as e:
                # Обробляємо помилки (наприклад, порожній кошик)
                messages.error(request, str(e))
                return redirect('basket:basket_detail')
        else:
            # Показуємо помилки валідації форми
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка в полі '{field}': {error}")
            return redirect('basket:basket_detail')
    # Якщо не POST запит - повертаємося до кошика
    return redirect('basket:basket_detail')


@login_required
def order_detail(request, order_id):
    """Відображає детальну інформацію про замовлення"""
    # Знаходимо замовлення за ID та перевіряємо власника
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        'orders/detail.html',
        {
            'order': order,  # Дані замовлення з товарами
            'categories': Category.objects.all(),  # Категорії для навігації
            'brands': Brand.objects.all()  # Бренди для навігації
        }
    )


@login_required
def payment_form(request, order_id):
    """Відображає форму оплати LiqPay"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Перевіряємо чи вже є активний платіж
    existing_payment = Payment.objects.filter(
        order=order,
        status__in=['pending', 'sandbox', 'success']
    ).first()

    if existing_payment and existing_payment.status == 'success':
        messages.info(request, 'Замовлення вже оплачено!')
        return redirect('orders:order_detail', order_id=order.id)

    # Створюємо новий платіж або використовуємо існуючий
    liqpay_service = LiqPayService()
    if not existing_payment:
        success_url = request.build_absolute_uri(
            reverse('orders:payment_success', kwargs={'order_id': order.id})
        )
        server_url = request.build_absolute_uri(
            reverse('orders:payment_callback')
        )

        payment = liqpay_service.create_payment(order, success_url, server_url)
    else:
        payment = existing_payment

    # Генеруємо форму для оплати
    success_url = request.build_absolute_uri(
        reverse('orders:payment_success', kwargs={'order_id':order.id})
    )
    server_url = request.build_absolute_uri(
        reverse('orders:payment_callback')
    )

    form_data = liqpay_service.get_payment_form_data(payment, success_url, server_url)

    return render(request, 'orders/payment_form.html', {
        'order': order,
        'payment': payment,
        'form_data': form_data,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all()
    })


@login_required
def payment_success(request, order_id):
    """Сторінка успішної оплати"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = Payment.objects.filter(order=order).last()

    return render(request, 'orders/payment_success.html', {
        'order': order,
        'payment': payment,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all()
    })


@csrf_exempt
@require_http_methods(["POST"])
def payment_callback(request):
    """Обробка callback від LiqPay"""
    data = request.POST.get('data')
    signature = request.POST.get('signature')

    if not data or not signature:
        logger.error("Callback без data або signature")
        return HttpResponse('Missing data or signature', status=400)

    liqpay_service = LiqPayService()
    result = liqpay_service.process_callback(data, signature)

    if result['status'] == 'success':
        logger.info(f'Callback успішно оброблено: {result}')
        return HttpResponse('OK')
    else:
        logger.error(f'Помилка при обробці callback: {result}')
        return HttpResponse('Error', status=400)














