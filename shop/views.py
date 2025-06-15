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

    # Логіка для рекомендацій на основі переглядів #777
    recommended_products = None  # 777
    session_key = f'recommended_products_{request.user.id}' if request.user.is_authenticated else 'recommended_products_guest'  # 777
    if request.user.is_authenticated:  # 777
        viewed_product_ids = cache.get(f'viewed_products_{request.user.id}', [])  # 777
        if viewed_product_ids and request.session.get('product_viewed', False):  # 777
            # Отримуємо переглянуті товари #777
            viewed_products = Product.objects.filter(id__in=viewed_product_ids, available=True)  # 777
            # Отримуємо унікальні комбінації категорій і брендів #777
            viewed_combinations = viewed_products.values('category_id', 'brand_id').distinct()  # 777
            # Формуємо Q-об'єкти для комбінацій #777
            query = Q()  # 777
            for combo in viewed_combinations:  # 777
                query |= Q(category_id=combo['category_id'], brand_id=combo['brand_id'])  # 777
            # Вибираємо до 5 випадкових товарів із комбінацій #777
            recommended_products = Product.objects.filter(  # 777
                query, available=True  # 777
            ).exclude(id__in=viewed_product_ids).order_by('?')[:6]  # 777
            # Зберігаємо рекомендації в сесії #777
            request.session[session_key] = [p.id for p in recommended_products]  # 777
            request.session['product_viewed'] = False  # 777
        else:  # 777
            # Використовуємо кешовані рекомендації, якщо є #777
            recommended_product_ids = request.session.get(session_key, [])  # 777
            if recommended_product_ids:  # 777
                recommended_products = Product.objects.filter(id__in=recommended_product_ids, available=True)  # 777
            # Якщо немає переглянутих товарів, рекомендації не показуємо #777

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
    # Зберігаємо ID переглянутого товару в Redis для рекомендацій #777
    if request.user.is_authenticated:  # 777
        viewed_products = cache.get(f'viewed_products_{request.user.id}', [])  # 777
        if product.id not in viewed_products:  # 777
            viewed_products.append(product.id)  # 777
            if len(viewed_products) > 10:  # 777
                viewed_products.pop(0)  # 777
            cache.set(f'viewed_products_{request.user.id}', viewed_products, timeout=3600 * 24 * 30)  # 777
        request.session['product_viewed'] = True  # 777
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


@login_required  # Требует, чтобы пользователь был авторизован
def create_order(request):  # Функция для создания заказа
    basket = get_object_or_404(Basket, user=request.user)  # Получает корзину пользователя или 404, если нет
    if not basket.items.exists():  # Проверяет, есть ли товары в корзине
        messages.error(request,
                       'Ваш кошик порожній. Додайте товари перед оформленням замовлення.')  # Сообщение об ошибке, если корзина пуста
        return redirect('shop:basket_detail')  # Перенаправляет на страницу корзины

    if request.method == 'POST':  # Проверяет, что запрос — POST (форма отправлена)
        form = OrderForm(request.POST)  # Создает форму с данными из запроса
        if form.is_valid():  # Проверяет, валидна ли форма
            order = form.save(commit=False)  # Создает заказ, но не сохраняет в БД
            order.user = request.user  # Привязывает заказ к текущему пользователю
            order.address = f"{form.cleaned_data['city']}, {form.cleaned_data['address']}"  # Формирует адрес из города и отделения
            order.address_ref = form.cleaned_data['address_ref']  # Сохраняет ref отделения Новой Почты
            order.save()  # Сохраняет заказ в БД

            for item in basket.items.all():  # Перебирает все товары в корзине
                OrderItem.objects.create(  # Создает элемент заказа для каждого товара
                    order=order,  # Привязывает к заказу
                    product=item.product,  # Указывает продукт
                    price=item.product.price,  # Фиксирует цену
                    quantity=item.quantity  # Указывает количество
                )

            basket.items.all().delete()  # Удаляет все товары из корзины
            messages.success(request, f'Замовлення #{order.id} успішно створено!')  # Сообщение об успешном создании
            return redirect('shop:product_list')  # Перенаправляет на список товаров
        else:  # Если форма невалидна
            for field, errors in form.errors.items():  # Перебирает ошибки формы
                for error in errors:  # Для каждой ошибки
                    messages.error(request, f"Помилка в полі '{field}': {error}")  # Выводит сообщение об ошибке
            return redirect('shop:basket_detail')  # Перенаправляет на страницу корзины


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
