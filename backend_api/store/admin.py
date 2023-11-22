from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'description', 
        'is_subcategory'
    ]
    list_filter = [
        'is_subcategory'
    ]
    prepopulated_fields = {
        'slug': ('title',)
    }
admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = [
        'title',
        'description',
        'price', 
        'is_available',
        'stock', 
        'category',
    ]
    list_filter = [
        'category',
        'is_available',        
    ]
    prepopulated_fields = {
        'slug': ('title',)
    }
    search_fields = [
        'title',
    ]
    readonly_fields = ('product_image',)

    def product_image(self, obj):
        # Метод для отображения изображения пользователя в виде тега HTML
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.photo.url)
    
    product_image.short_description = 'Image'
admin.site.register(Product, ProductAdmin)
    