from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .services import ReviewService
from products.models import Product
from shop.forms import ReviewForm
from django.views.decorators.http import require_POST


@login_required
@require_POST
def create_review(request, product_id):
    """Створює новий відгук для товару"""
    # Отримуємо товар за ID
    product = get_object_or_404(Product, id=product_id)
    # Валідуємо форму відгуку
    review_form = ReviewForm(request.POST)

    if review_form.is_valid():
        # Створюємо відгук через ReviewService
        review, success, error_message = ReviewService.create_review(
            user=request.user,
            product=product,
            comment=review_form.cleaned_data['comment']
        )

        if success:
            messages.success(request, 'Відгук успішно додано!')
        else:
            # Показуємо помилку (наприклад, користувач вже залишив відгук)
            messages.error(request, error_message)
    else:
        messages.error(request, 'Помилка у формі відгуку.')

    return redirect('products:product_detail', category_slug=product.category.slug, product_slug=product.slug)


@login_required
@require_POST
def delete_review(request, review_id):
    """Видаляє відгук користувача (тільки власні відгуки)"""
    # Використовуємо сервіс для видалення відгуку
    success, product, error_message = ReviewService.delete_review(request.user, review_id)

    if success:
        messages.success(request, 'Відгук успішно видалено!')
        # Повертаємося на сторінку товару для перегляду оновленого списку відгуків
        return redirect('products:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    else:
        # Показуємо помилку (наприклад, немає прав для видалення)
        messages.error(request, error_message)
        return redirect('products:product_list')
