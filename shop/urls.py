from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='shop/account/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop:product_list'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]




