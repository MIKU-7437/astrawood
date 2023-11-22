from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = '__all__'


class Cart(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
