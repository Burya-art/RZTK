from shop.models import Category, Brand


def categories_and_brands(request):
    return {
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
