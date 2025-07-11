from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from shop.forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from orders.models import Order


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('account:profile')
        else:
            form = UserRegisterForm(request.POST)
    else:
        form = UserRegisterForm()
    return render(request, 'account/register.html', {'form': form})


def user_login(request):
    """Власний view для входу з підтримкою email замість username"""
    if request.method == 'POST':
        email = request.POST.get('username')  # Поле називається username але містить email
        password = request.POST.get('password')
        
        # Аутентифікація через email
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user, backend='account.backends.EmailBackend')
            messages.success(request, 'Ви успішно увійшли!')
            return redirect('account:profile')
        else:
            messages.error(request, 'Невірний email або пароль.')
            
        # Створюємо форму з помилками для відображення
        form = AuthenticationForm()
        form.add_error('username', 'Невірний email або пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'account/custom_login.html', {'form': form})


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by(
        '-created')  # Отримуємо замовлення користувача, сортуємо за датою (нові зверху)
    return render(
        request,
        'account/profile.html',
        {'user': request.user, 'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if request.method == 'POST' and order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Замовлення скасовано.')
    return redirect('account:profile')


