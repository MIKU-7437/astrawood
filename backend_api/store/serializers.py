from rest_framework import serializers
from .models import Category, Product

class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            'title',
            'slug',
            'description',
        ]

class CategorySerializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'title',
            'slug',
            'description',
            'sub_categories',
        ]
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title',
            'slug',
            'price',
            'is_available',
            'description',
            'stock',
            'category',
            'photo',
        ]
        depth = 1
