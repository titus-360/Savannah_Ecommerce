from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    average_price = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'parent_name', 'description', 
                 'children', 'average_price', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_children(self, obj):
        children = obj.get_children()
        return CategorySerializer(children, many=True).data

    def get_average_price(self, obj):
        return obj.get_average_price()

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_path = serializers.CharField(source='get_category_path', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name',
                 'category_path', 'stock', 'created_at', 'updated_at', 'image']
        read_only_fields = ['category_name', 'category_path', 'created_at', 'updated_at'] 