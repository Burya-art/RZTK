from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from shop.forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Order


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('account:profile')
        else:
            messages.error(request, 'Error during registration. Please check the form.')
    else:
        form = UserRegisterForm()
    return render(request, 'shop/account/register.html', {'form': form})


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by(
        '-created')  # Отримуємо замовлення користувача, сортуємо за датою (нові зверху)
    return render(
        request,
        'shop/account/profile.html',
        {'user': request.user, 'orders': orders})
