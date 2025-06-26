from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from .services import create_order_from_basket
from products.models import Category, Brand
from shop.forms import OrderForm
from nova_poshta.services import NovaPoshtaService
from rztk_project.settings import NOVA_POSHTA_API_KEY
import logging

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
                    city=form.cleaned_data['city'],        # Місто доставки
                    address=form.cleaned_data['address'],  # Адреса відділення
                    address_ref=form.cleaned_data['address_ref']  # ID відділення Нової Пошти
                )
                messages.success(request, f'Замовлення #{order.id} успішно створено!')
                # Після успішного замовлення повертаємося до каталогу
                return redirect('products:product_list')
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
            'order': order,                     # Дані замовлення з товарами
            'categories': Category.objects.all(), # Категорії для навігації
            'brands': Brand.objects.all()        # Бренди для навігації
        }
    )
