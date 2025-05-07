from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        ordering = ['name']
        db_table = 'brands'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list', kwargs={'brand': self.slug})


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['name']
        db_table = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products',
                                 on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products',
                              on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d',
                              blank=True, null=True)

    class Meta:
        # ordering = ['name']
        ordering = ['created']
        db_table = 'products'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.category.slug, self.slug])


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'baskets'
        verbose_name = 'basket'
        verbose_name_plural = 'baskets'

    def __str__(self):
        return f'Basket for {self.user.username}'


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='basket_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'basket_items'
        verbose_name = 'basket item'
        verbose_name_plural = 'basket items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_total_price(self):
        return self.quantity * self.product.price
