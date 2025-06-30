from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')
    comment = models.TextField(blank=True, verbose_name='')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created']
        unique_together = ['product', 'user']

    def __str__(self):
        return f'Відгук від {self.user.username} на {self.product.name}'
