from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import BasketService
from products.models import Product, Category, Brand
from shop.forms import BasketItemForm, OrderForm


@login_required
def add_to_basket(request, product_id):
    """Додає товар до кошика користувача"""
    if request.method == 'POST':
        # Перевіряємо що товар існує
        product = get_object_or_404(Product, id=product_id)
        # Додаємо товар до кошика через сервіс
        BasketService.add_product_to_basket(request.user, product_id)
        messages.success(request, 'Товар успішно додано до кошика!')
        # Повертаємося на сторінку товару
        return redirect('products:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    # Якщо не POST запит - повертаємося до списку товарів
    return redirect('products:product_list')


@login_required
def basket_detail(request):
    """Відображає детальну інформацію про кошик з формою замовлення"""
    # Отримуємо кошик користувача (створюємо якщо не існує)
    basket = BasketService.get_or_create_basket(request.user)
    # Обчислюємо загальну вартість усіх товарів в кошику
    total_price = BasketService.get_basket_total_price(request.user)
    # Підготовлюємо форму для оформлення замовлення
    order_form = OrderForm()
    return render(request, 'basket/detail.html',
                  {
                      'basket': basket,                    # Кошик з товарами
                      'total_price': total_price,          # Загальна сума
                      'order_form': order_form,            # Форма замовлення
                      'categories': Category.objects.all(), # Категорії для навігації
                      'brands': Brand.objects.all()        # Бренди для навігації
                  })


@login_required
def update_basket_item(request, item_id):
    """Оновлює кількість товару в кошику"""
    if request.method == 'POST':
        # Валідуємо дані з форми зміни кількості
        form = BasketItemForm(request.POST)
        if form.is_valid():
            # Оновлюємо кількість товару через сервіс
            BasketService.update_basket_item_quantity(
                request.user,
                item_id,
                form.cleaned_data['quantity']  # Нова кількість з форми
            )
            messages.success(request, 'Кількість товару оновлено!')
        else:
            messages.error(request, 'Помилка при оновленні кількості.')
    # Повертаємося до сторінки кошика
    return redirect('basket:basket_detail')


@login_required
def remove_from_basket(request, item_id):
    """Видаляє конкретний товар з кошика"""
    if request.method == 'POST':
        # Видаляємо товар з кошика через сервіс
        BasketService.remove_item_from_basket(request.user, item_id)
        messages.success(request, 'Товар видалено з кошика!')
    # Повертаємося до сторінки кошика
    return redirect('basket:basket_detail')


@login_required
def clear_basket(request):
    """Очищає весь кошик користувача"""
    if request.method == 'POST':
        # Видаляємо всі товари з кошика через сервіс
        BasketService.clear_basket(request.user)
        messages.success(request, 'Кошик успішно очищено!')
    # Повертаємося до сторінки кошика
    return redirect('basket:basket_detail')
