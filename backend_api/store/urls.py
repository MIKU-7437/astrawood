from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

# router = DefaultRouter()
# router.register(r'category', CategoryViewSet, basename="category")
# router.register(r'product', ProductViewSet, basename="product")
# path('', include(router.urls)),
urlpatterns = [
    path('category/', CategoryViewSet.as_view({'get': 'list'}), name='category-list'),
    path('category/<slug:category_slug>/', CategoryViewSet.as_view({'get': 'retrieve'}), name='category-detail'),
    path('category/<slug:category_slug>/product/', CategoryViewSet.as_view({'get': 'product_list'}), name='category-product-list'),
    path('category/<slug:category_slug>/product/<slug:product_slug>/', ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]