from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Category, Brand, Product, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BasketItemForm, OrderForm, ReviewForm
from django.views.decorators.csrf import csrf_exempt
from .services.nova_poshta import NovaPoshtaService
from rztk_project.settings import NOVA_POSHTA_API_KEY
import logging
from django.core.exceptions import PermissionDenied
from .services.order import create_order_from_basket
from .services.basket import BasketService
from .services.product import ProductService
from .services.review import ReviewService

logger = logging.getLogger(__name__)

# Инициализация NovaPoshtaService
nova_poshta_service = NovaPoshtaService(NOVA_POSHTA_API_KEY)
logger.debug(f"NOVA_POSHTA_API_KEY: {NOVA_POSHTA_API_KEY}")


def product_list(request, category_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    search_query = request.GET.get('q')

    # Отримуємо рекомендовані продукти
    recommended_products = ProductService.get_recommended_products(request.user)

    # Валідуємо ціновий діапазонн
    price_min, price_max, price_errors = ProductService.validate_price_range(
        request.GET.get('price_min'),
        request.GET.get('price_max')
    )

    # Додаємо помилки валідації цін
    for error in price_errors:
        messages.error(request, error)

    # Отримуємо відфільтровані продукти
    products = ProductService.get_filtered_products(
        category_slug=category_slug or request.GET.get('category'),
        brand_slug=request.GET.get('brand'),
        search_query=search_query,
        price_min=price_min,
        price_max=price_max,
        sort_by=request.GET.get('sort')
    )

    # Отримуємо категорію та бренд для контексту
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    elif request.GET.get('category'):
        category = get_object_or_404(Category, slug=request.GET.get('category'))

    if request.GET.get('brand'):
        brand = get_object_or_404(Brand, slug=request.GET.get('brand'))

    # Пагінація
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'brand': brand,
            'brands': brands,
            'products': products,
            'search_query': search_query,
            'recommended_products': recommended_products,
        })


def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = ProductService.get_product_by_slug(category_slug, product_slug)

    # Відстежуємо перегляд продукту
    ProductService.track_product_view(request.user, product)

    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review, success, error_message = ReviewService.create_review(
                user=request.user,
                product=product,
                rating=review_form.cleaned_data.get('rating', 5),
                comment=review_form.cleaned_data['comment']
            )

            if success:
                messages.success(request, 'Відгук успішно додано!')
                return redirect('shop:product_detail', category_slug=category_slug, product_slug=product_slug)
            else:
                messages.error(request, error_message)

    return render(
        request,
        'shop/product/detail.html',
        {
            'category': category,
            'product': product,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'review_form': review_form,
            'reviews': ReviewService.get_product_reviews(product)
        })


@login_required
def add_to_basket(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        BasketService.add_product_to_basket(request.user, product_id)
        messages.success(request, 'Товар успішно додано до кошика!')
        return redirect('shop:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    return redirect('shop:product_list')


@login_required
def basket_detail(request):
    basket = BasketService.get_or_create_basket(request.user)
    total_price = BasketService.get_basket_total_price(request.user)
    order_form = OrderForm()
    return render(request, 'shop/basket/detail.html',
                  {
                      'basket': basket,
                      'total_price': total_price,
                      'order_form': order_form,
                      'categories': Category.objects.all(),
                      'brands': Brand.objects.all()
                  })


@login_required
def update_basket_item(request, item_id):
    if request.method == 'POST':
        form = BasketItemForm(request.POST)
        if form.is_valid():
            BasketService.update_basket_item_quantity(
                request.user,
                item_id,
                form.cleaned_data['quantity']
            )
            messages.success(request, 'Кількість товару оновлено!')
        else:
            messages.error(request, 'Помилка при оновленні кількості.')
    return redirect('shop:basket_detail')


@login_required
def remove_from_basket(request, item_id):
    if request.method == 'POST':
        BasketService.remove_item_from_basket(request.user, item_id)
        messages.success(request, 'Товар видалено з кошика!')
    return redirect('shop:basket_detail')


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = create_order_from_basket(
                    user=request.user,
                    city=form.cleaned_data['city'],
                    address=form.cleaned_data['address'],
                    address_ref=form.cleaned_data['address_ref']
                )
                messages.success(request, f'Замовлення #{order.id} успішно створено!')
                return redirect('shop:product_list')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('shop:basket_detail')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка в полі '{field}': {error}")
            return redirect('shop:basket_detail')
    return redirect('shop:basket_detail')


@login_required
def clear_basket(request):
    if request.method == 'POST':
        BasketService.clear_basket(request.user)
        messages.success(request, 'Кошик успішно очищено!')
    return redirect('shop:basket_detail')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        'shop/order/detail.html',
        {
            'order': order,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all()
        }
    )


@login_required
@csrf_exempt
def get_nova_poshta_cities(request):
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': "Місто обов'язкове"}, status=400)

    cities = nova_poshta_service.get_cities(city)
    logger.debug(f"Returned cities for {city}: {cities}")
    return JsonResponse({'cities': cities})


@login_required
@csrf_exempt
def get_nova_poshta_warehouses(request):
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': "Місто обов'язкове"}, status=400)

    warehouses = nova_poshta_service.get_warehouses(city)
    logger.debug(f"Returned warehouses for {city}: {warehouses}")
    return JsonResponse({'warehouses': warehouses})


@login_required
def delete_review(request, review_id):
    if request.method == 'POST':
        success, product, error_message = ReviewService.delete_review(request.user, review_id)

        if success:
            messages.success(request, 'Відгук успішно видалено!')
            return redirect('shop:product_detail', category_slug=product.category.slug, product_slug=product.slug)
        else:
            messages.error(request, error_message)
            return redirect('shop:product_list')

    raise PermissionDenied
