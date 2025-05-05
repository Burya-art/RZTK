from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Brand, Product
from django.db.models import Q


def product_list(request, category_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)

    # Получаем поисковый запрос
    if search_query := request.GET.get('q'):
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Фильтрация по категории через URL
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Фильтрация через GET-параметры
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
