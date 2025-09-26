from rest_framework import serializers

from store.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ListProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=False, read_only=True)
    created_by_seller = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'created_at', 'created_by_seller']


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'created_by_seller']
