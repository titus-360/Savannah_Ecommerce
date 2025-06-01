from django.db import models
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class MPTTMeta:
        order_insertion_by = ['name']
        parent_attr = 'parent'

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def get_ancestors_path(self):
        """Returns the full path of ancestors for this category"""
        return ' > '.join([ancestor.name for ancestor in self.get_ancestors(include_self=True)])

    def get_all_products(self):
        """Returns all products in this category and its descendants"""
        return Product.objects.filter(category__in=self.get_descendants(include_self=True))

    def get_average_price(self):
        """Returns the average price of all products in this category and its descendants"""
        products = self.get_all_products()
        if not products:
            return 0
        return sum(product.price for product in products) / len(products)

    def clean(self):
        """Prevent circular references in the category hierarchy"""
        if self.parent and self.parent.is_descendant_of(self):
            raise ValidationError("A category cannot be a parent of its own ancestor.")

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_category_path(self):
        """Returns the full category path for this product"""
        return self.category.get_ancestors_path()
