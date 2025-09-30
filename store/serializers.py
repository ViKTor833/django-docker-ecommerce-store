from rest_framework import serializers

from store.models import Category, Product, Cart, CartItem


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


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']


class CartSerializer(serializers.ModelSerializer):
    created_by_customer = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'date_created', 'created_by_customer']


class CartItemSerializer(serializers.ModelSerializer):
    productItem = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.productItem.price

    class Meta:
        model = CartItem
        fields = ['id', 'productItem', 'quantity', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    productItem_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart = self.context['cart']
        productItem_id = self.validated_data['productItem_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart=cart, productItem_id=productItem_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart=cart, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'productItem_id', 'quantity']

    def validate_productItemd_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class UpdateCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.productItem.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'date_created', 'items', 'total_price']
