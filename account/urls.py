from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, user_login, profile, cancel_order

app_name = 'account'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),  # Наш власний view
    path('logout/', LogoutView.as_view(next_page='products:product_list'), name='logout'),
    path('profile/', profile, name='profile'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
]



