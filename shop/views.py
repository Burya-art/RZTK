from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Category, Brand, Product, Basket, BasketItem, Order, OrderItem, Review
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .forms import BasketItemForm, OrderForm, ReviewForm
from django.views.decorators.csrf import csrf_exempt
from .services.nova_poshta import NovaPoshtaService
from rztk_project.settings import NOVA_POSHTA_API_KEY
import logging
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from .services.order import create_order_from_basket

logger = logging.getLogger(__name__)

# Инициализация NovaPoshtaService
nova_poshta_service = NovaPoshtaService(NOVA_POSHTA_API_KEY)
logger.debug(f"NOVA_POSHTA_API_KEY: {NOVA_POSHTA_API_KEY}")


def product_list(request, category_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)

    # Логіка для рекомендацій на основі переглядів
    recommended_products = None
    if request.user.is_authenticated:
        # Отримуємо список ID переглянутих товарів з Redis
        viewed_product_ids = cache.get(f'viewed_products_{request.user.id}', [])
        # Ключ для зберігання рекомендацій у Redis
        cache_key = f'recommended_products_{request.user.id}'
        # Перевіряємо, чи є переглянуті товари і чи був нещодавній перегляд товару
        if viewed_product_ids and cache.get(f'product_viewed_{request.user.id}', False):
            # Отримуємо переглянуті товари з бази
            viewed_products = Product.objects.filter(id__in=viewed_product_ids, available=True)
            # Отримуємо унікальні комбінації категорій і брендів переглянутих товарів
            viewed_combinations = viewed_products.values('category_id', 'brand_id').distinct()
            # Формуємо запит для пошуку товарів з тих же категорій і брендів
            query = Q()
            for combo in viewed_combinations:
                query |= Q(category_id=combo['category_id'], brand_id=combo['brand_id'])
            # Вибираємо до 6 випадкових товарів, виключаючи переглянуті
            recommended_products = Product.objects.filter(query, available=True).exclude(
                id__in=viewed_product_ids).order_by('?')[:6]
            # Зберігаємо ID рекомендованих товарів у Redis на 30 днів
            cache.set(cache_key, [p.id for p in recommended_products], timeout=3600 * 24 * 30)
            # Скидаємо позначку перегляду товару
            cache.set(f'product_viewed_{request.user.id}', False, timeout=3600 * 24 * 30)
        else:
            # Отримуємо кешовані рекомендації з Redis, якщо вони є
            recommended_product_ids = cache.get(cache_key, [])
            if recommended_product_ids:
                # Завантажуємо рекомендовані товари з бази
                recommended_products = Product.objects.filter(id__in=recommended_product_ids, available=True)

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

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min or price_max:
        try:
            if price_min:
                price_min = float(price_min)
                if price_min < 0:
                    messages.error(request, 'Мінімальна ціна не може бути від’ємною.')
                    price_min = None
            else:
                price_min = None
            if price_max:
                price_max = float(price_max)
                if price_max < 0:
                    messages.error(request, 'Максимальна ціна не може бути від’ємною.')
                    price_max = None
            else:
                price_max = None
            if price_min is not None and price_max is not None and price_min > price_max:
                messages.error(request, 'Мінімальна ціна не може бути більшою за максимальну.')
            elif price_min is not None or price_max is not None:
                if price_min is not None:
                    products = products.filter(price__gte=price_min)
                if price_max is not None:
                    products = products.filter(price__lte=price_max)
        except ValueError:
            messages.error(request, 'Некоректний формат цін.')

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

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
    product = get_object_or_404(Product, category=category, slug=product_slug, available=True)
    # Зберігаємо ID переглянутого товару в Redis
    if request.user.is_authenticated:
        # Отримуємо список переглянутих товарів з Redis
        viewed_products = cache.get(f'viewed_products_{request.user.id}', [])
        # Додаємо ID поточного товару, якщо його ще немає
        if product.id not in viewed_products:
            viewed_products.append(product.id)
            # Обмежуємо список до 10 товарів
            if len(viewed_products) > 10:
                viewed_products.pop(0)
            # Зберігаємо оновлений список у Redis на 30 днів
            cache.set(f'viewed_products_{request.user.id}', viewed_products, timeout=3600 * 24 * 30)
        # Позначка, що товар був переглянутий (для оновлення рекомендацій)
        cache.set(f'product_viewed_{request.user.id}', True, timeout=3600 * 24 * 30)
    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            try:
                review.save()
                messages.success(request, 'Відгук успішно додано!')
                return redirect('shop:product_detail', category_slug=category_slug, product_slug=product_slug)
            except IntegrityError:
                messages.error(request, 'Ви вже залишили відгук для цього товару.')

    return render(
        request,
        'shop/product/detail.html',
        {
            'category': category,
            'product': product,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'review_form': review_form,
            'reviews': product.reviews.all()
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
        return redirect('shop:product_detail', category_slug=product.category.slug, product_slug=product.slug, )
    return redirect('shop:product_list')


@login_required
def basket_detail(request):
    basket, created = Basket.objects.get_or_create(user=request.user)
    total_price = sum(item.get_total_price() for item in basket.items.all())
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
    basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=request.user)
    if request.method == 'POST':
        basket_item.delete()
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


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        product = review.product
        review.delete()
        messages.success(request, 'Відгук успішно видалено!')
        return redirect('shop:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    raise PermissionDenied
