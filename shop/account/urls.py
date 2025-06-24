from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from shop.account.views import register, profile, cancel_order

app_name = 'account'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='shop/account/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='products:product_list'), name='logout'),
    path('profile/', profile, name='profile'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
]


