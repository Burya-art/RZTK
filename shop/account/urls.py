from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from ..views import register, profile

app_name = 'account'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='shop/account/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop:product_list'), name='logout'),
    path('profile/', profile, name='profile'),
]
