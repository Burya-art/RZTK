from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import BasketService
from products.models import Product, Category, Brand
from shop.forms import BasketItemForm, OrderForm


@login_required
def add_to_basket(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        BasketService.add_product_to_basket(request.user, product_id)
        messages.success(request, 'Товар успішно додано до кошика!')
        return redirect('products:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    return redirect('products:product_list')


@login_required
def basket_detail(request):
    basket = BasketService.get_or_create_basket(request.user)
    total_price = BasketService.get_basket_total_price(request.user)
    order_form = OrderForm()
    return render(request, 'basket/detail.html',
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
    return redirect('basket:basket_detail')


@login_required
def remove_from_basket(request, item_id):
    if request.method == 'POST':
        BasketService.remove_item_from_basket(request.user, item_id)
        messages.success(request, 'Товар видалено з кошика!')
    return redirect('basket:basket_detail')


@login_required
def clear_basket(request):
    if request.method == 'POST':
        BasketService.clear_basket(request.user)
        messages.success(request, 'Кошик успішно очищено!')
    return redirect('basket:basket_detail')
