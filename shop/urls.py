from django.urls import path
from django.shortcuts import redirect

app_name = 'shop'


def redirect_to_products(request):
    return redirect('products:product_list')


urlpatterns = [
    # Редирект на products app
    path('', redirect_to_products, name='product_list'),
]
