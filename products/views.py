from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Category, Brand, Product
from .services import ProductService
from reviews.services import ReviewService
from reviews.models import Review
from shop.forms import ReviewForm


def product_list(request, category_slug=None):
    """Відображає список продуктів з фільтрами та пошуком"""
    # Ініціалізуємо змінні для контексту
    category = None
    brand = None
    categories = Category.objects.all()  # Всі категорії для сайдбару
    brands = Brand.objects.all()         # Всі бренди для сайдбару
    search_query = request.GET.get('q')  # Пошуковий запит з форми

    # Отримуємо персональні рекомендації на основі переглядів користувача
    recommended_products = ProductService.get_recommended_products(request.user)

    # Перевіряємо коректність введених цін (мін/макс)
    price_min, price_max, price_errors = ProductService.validate_price_range(
        request.GET.get('price_min'),
        request.GET.get('price_max')
    )

    # Показуємо користувачу помилки валідації цін
    for error in price_errors:
        messages.error(request, error)

    # Застосовуємо всі фільтри та отримуємо відфільтровані продукти
    products = ProductService.get_filtered_products(
        category_slug=category_slug or request.GET.get('category'),  # Категорія з URL або GET
        brand_slug=request.GET.get('brand'),    # Бренд з GET параметрів
        search_query=search_query,              # Текст пошуку
        price_min=price_min,                    # Мінімальна ціна
        price_max=price_max,                    # Максимальна ціна
        sort_by=request.GET.get('sort')         # Сортування (ціна вгору/вниз)
    )

    # Визначаємо активну категорію та бренд для підсвічування в інтерфейсі
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    elif request.GET.get('category'):
        category = get_object_or_404(Category, slug=request.GET.get('category'))

    if request.GET.get('brand'):
        brand = get_object_or_404(Brand, slug=request.GET.get('brand'))

    # Розбиваємо результати на сторінки (по 9 товарів)
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)         # Запитана сторінка
    except PageNotAnInteger:
        products = paginator.page(1)           # Якщо номер сторінки некоректний -> перша
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # Якщо сторінка не існує -> остання

    return render(
        request,
        'products/list.html',
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
    """Відображає детальну сторінку продукту з відгуками та формою додавання відгуку"""
    # Отримуємо категорію та продукт за slug'ами з URL
    category = get_object_or_404(Category, slug=category_slug)
    product = ProductService.get_product_by_slug(category_slug, product_slug)

    # Зберігаємо інформацію про перегляд для рекомендацій
    ProductService.track_product_view(request.user, product)

    # Підготовлюємо порожню форму для нового відгуку
    review_form = ReviewForm()

    # Відображаємо шаблон з усіма даними
    return render(
        request,
        'products/detail.html',
        {
            'category': category,                               # Поточна категорія продукту
            'product': product,                                 # Дані продукту
            'categories': Category.objects.all(),              # Всі категорії для навігації
            'brands': Brand.objects.all(),                     # Всі бренди для навігації  
            'review_form': review_form,                        # Форма для додавання відгуку
            'reviews': ReviewService.get_product_reviews(product)  # Список всіх відгуків продукту
        })
