from django.shortcuts import render, get_object_or_404
from .models import Category, Brand, Product


def product_list(request, category_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)

    # Фильтрация по категории через URL
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Фильтрация через GET-параметры
    category_filter = request.GET.get('category')
    brand_filter = request.GET.get('brand')

    if category_filter:
        category = get_object_or_404(Category, slug=category_filter)
        products = products.filter(category=category)

    if brand_filter:
        brand = get_object_or_404(Brand, slug=brand_filter)
        products = products.filter(brand=brand)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'brand': brand,
        'brands': brands,
        'products': products
    })


def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, category=category, slug=product_slug, available=True)

    return render(request, 'shop/product/detail.html', {
        'category': category,
        'product': product
    })
