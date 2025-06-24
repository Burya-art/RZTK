from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .services import ReviewService


@login_required
def delete_review(request, review_id):
    if request.method == 'POST':
        success, product, error_message = ReviewService.delete_review(request.user, review_id)

        if success:
            messages.success(request, 'Відгук успішно видалено!')
            return redirect('products:product_detail', category_slug=product.category.slug, product_slug=product.slug)
        else:
            messages.error(request, error_message)
            return redirect('products:product_list')

    raise PermissionDenied
