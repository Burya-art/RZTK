from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Category, Brand, Product
from .services import ProductService
from reviews.services import ReviewService
from reviews.models import Review
from shop.forms import ReviewForm


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
                return redirect('products:product_detail', category_slug=category_slug, product_slug=product_slug)
            else:
                messages.error(request, error_message)

    return render(
        request,
        'products/detail.html',
        {
            'category': category,
            'product': product,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'review_form': review_form,
            'reviews': ReviewService.get_product_reviews(product)
        })
