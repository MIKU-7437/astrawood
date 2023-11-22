from django.db import models
from store.models import Product
from users.models import User

from django.core.validators import MinValueValidator


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    quantity =  models.IntegerField(validators=[MinValueValidator(limit_value=1)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)