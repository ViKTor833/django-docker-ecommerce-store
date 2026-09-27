from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from store.models import Category, Product, Cart, CartItem, Customer, Seller, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ListProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=False, read_only=True)
    created_by_seller = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'created_at', 'created_by_seller']


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']

    def save(self, **kwargs):
        created_by_seller = Seller.objects.get(user_id=self.context['user_id'])
        super().save(created_by_seller=created_by_seller, **kwargs)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    productItem = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.productItem.price

    class Meta:
        model = CartItem
        fields = ['id', 'productItem', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    created_by_customer = serializers.StringRelatedField(many=False, read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, cart):
        return sum([item.quantity * item.productItem.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'date_created', 'created_by_customer', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    productItem_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart = self.context['cart']
        productItem_id = self.validated_data['productItem_id']
        quantity = self.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(cart=cart, productItem_id=productItem_id,
                                                            defaults={'quantity': quantity})
        self.instance = cart_item
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'productItem_id', 'quantity']

    def validate_productItem_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birthday', 'phone']


class SellerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'user_id', 'phone']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class CreateOrderSerializer(serializers.Serializer):

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])

            cart = get_object_or_404(Cart, created_by_customer=customer)
            cart_items = CartItem.objects.select_related("productItem").filter(cart=cart)
            if not cart_items.exists():
                raise serializers.ValidationError('Cart is empty!')

            order = Order.objects.create(customer=customer)

            order_items = [OrderItem(
                order=order,
                product=item.productItem,
                product_name=item.productItem.name,
                price=item.productItem.price,
                quantity=item.quantity
            ) for item in cart_items]

            OrderItem.objects.bulk_create(order_items)
            cart.delete()

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
