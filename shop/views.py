from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Category, Brand, Product, Basket, BasketItem, Order, OrderItem
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BasketItemForm, OrderForm
from django.views.decorators.csrf import csrf_exempt
import environ
from .services.nova_poshta import NovaPoshtaService
import os
import logging

logger = logging.getLogger(__name__)

# Дебаг: виводимо шлях до .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(BASE_DIR, '.env')
print(f"Шлях до .env: {env_file_path}")

env = environ.Env()
environ.Env.read_env(env_file_path)

# Дебаг: виводимо значення NOVA_POSHTA_API_KEY
api_key = env('NOVA_POSHTA_API_KEY')
print(f"NOVA_POSHTA_API_KEY: {api_key}")

nova_poshta_service = NovaPoshtaService(api_key)

def product_list(request, category_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)

    if search_query := request.GET.get('q'):
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if category_filter := request.GET.get('category'):
        category = get_object_or_404(Category, slug=category_filter)
        products = products.filter(category=category)

    if brand_filter := request.GET.get('brand'):
        brand = get_object_or_404(Brand, slug=brand_filter)
        products = products.filter(brand=brand)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'brand': brand,
            'brands': brands,
            'products': products,
            'search_query': search_query
        })

def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, category=category, slug=product_slug, available=True)

    return render(
        request,
        'shop/product/detail.html',
        {
            'category': category,
            'product': product
        })

@login_required
def add_to_basket(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        basket, created = Basket.objects.get_or_create(user=request.user)

        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            basket_item.quantity += 1
            basket_item.save()

        messages.success(request, 'Товар успішно додано до кошика!')
        return redirect('shop:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    return redirect('shop:product_list')

@login_required
def basket_detail(request):
    basket, created = Basket.objects.get_or_create(user=request.user)
    total_price = sum(item.get_total_price() for item in basket.items.all())
    order_form = OrderForm()
    return render(request, 'shop/basket/detail.html',
                  {'basket': basket, 'total_price': total_price, 'order_form': order_form})

@login_required
def update_basket_item(request, item_id):
    basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=request.user)
    if request.method == 'POST':
        form = BasketItemForm(request.POST, instance=basket_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кількість товару оновлено!')
        else:
            messages.error(request, 'Помилка при оновленні кількості.')
    return redirect('shop:basket_detail')

@login_required
def remove_from_basket(request, item_id):
    basket_item = get_object_or_404(BasketItem, id=item_id,
                                    basket__user=request.user)
    if request.method == 'POST':
        basket_item.delete()
        messages.success(request, 'Товар видалено з кошика!')
    return redirect('shop:basket_detail')

@login_required
def create_order(request):
    basket = get_object_or_404(Basket, user=request.user)
    if not basket.items.exists():
        messages.error(
            request,
            'Ваш кошик порожній. Додайте товари перед оформленням замовлення.')
        return redirect('shop:basket_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.address = f"{form.cleaned_data['city']}, {form.cleaned_data['address']}"
            order.address_ref = form.cleaned_data['address_ref']
            order.save()

            for item in basket.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            basket.items.all().delete()
            messages.success(request, f'Замовлення #{order.id} успішно створено!')
            return redirect('shop:product_list')
        else:
            # Выводим ошибки валидации формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка в полі '{field}': {error}")
            return redirect('shop:basket_detail')

@login_required
def clear_basket(request):
    basket = get_object_or_404(Basket, user=request.user)
    if request.method == 'POST':
        basket.items.all().delete()
        messages.success(request, 'Кошик успішно очищено!')
    return redirect('shop:basket_detail')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        'shop/order/detail.html',
        {'order': order}
    )

@login_required
@csrf_exempt
def get_nova_poshta_cities(request):
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': 'Місто обов’язкове'}, status=400)

    cities = nova_poshta_service.get_cities(city)
    logger.debug(f"Returned cities for {city}: {cities}")
    return JsonResponse({'cities': cities})

@login_required
@csrf_exempt
def get_nova_poshta_warehouses(request):
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': 'Місто обов’язкове'}, status=400)

    warehouses = nova_poshta_service.get_warehouses(city)
    logger.debug(f"Returned warehouses for {city}: {warehouses}")
    return JsonResponse({'warehouses': warehouses})