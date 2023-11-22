from django.db import models


class Category(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=50, 
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )
    sub_categories = models.ManyToManyField(
        'self', 
        verbose_name='Подкатегории',
        blank=True,
        symmetrical=False, 
        related_name="top_catgeory",
    )
    is_subcategory = models.BooleanField(
        verbose_name='Подкатегория',
        default=False,
    )
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=50, 
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50, 
        unique=True,
    )
    price = models.IntegerField(
        verbose_name='Цена',
    )
    is_available = models.BooleanField(
        verbose_name='В наличии',
        default=True
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=500, 
        blank=True,
        null=True,
    )
    stock = models.IntegerField(
        verbose_name='Количество',
    )
    category = models.ForeignKey(
        Category, 
        verbose_name='Категория',
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    modified_date = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )
    photo = models.ImageField(
        verbose_name='Фотография',
        upload_to='product_photos/',
        blank=True,
        null=True,
    )


    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
