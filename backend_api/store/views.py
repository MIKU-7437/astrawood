from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().filter(is_subcategory=False)
    serializer_class = CategorySerializer
    lookup_field = 'slug'   

    def get_object(self):
        category_slug = self.kwargs['category_slug']
        return get_object_or_404(Category, slug=category_slug)

        
    @action(detail=True, methods=['get'])
    def product_list(self, request, category_slug):
        if Product.objects.filter(category__top_catgeory__slug=category_slug, is_available=True).exists():
            obj = Product.objects.filter(category__top_catgeory__slug=category_slug, is_available=True)
        else:
            obj = Product.objects.filter(category__slug=category_slug, is_available=True)
        serializer = ProductSerializer(obj, many=True)
        print(obj)
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_object(self):
        product_slug = self.kwargs['product_slug']
        return get_object_or_404(Product, slug=product_slug)


