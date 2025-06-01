from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'get_ancestors_path')
    list_filter = ('parent',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'get_category_path', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
