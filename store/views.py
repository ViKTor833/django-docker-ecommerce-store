from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from openid.server.trustroot import returnToMatches
from rest_framework import status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from store.forms import CustomerForm, ProductForm, SellerForm
from store.models import Product, Customer, Seller, Category, Cart, CartItem, Order, OrderItem
from store.permissions import IsAdminOrReadOnly, IsCustomerUser, IsSellerUser
from store.serializers import CategorySerializer, CreateProductSerializer, ListProductSerializer, CartSerializer, \
    CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, \
    SellerSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer
from .decorators import admin_required, seller_required, customer_required


# Create your views here.
def home(request):
    products = Product.objects.all()
    filter_type = request.GET.get('filter_type', '')
    search_field = request.GET.get('search_field')
    filter_categories = request.GET.getlist('filter_categories')

    if filter_categories.__len__() != 0:
        products = products.filter(category__in=filter_categories)

    if filter_type == 'newest':
        products = products.order_by('-created_at')
    elif filter_type == 'oldest':
        products = products.order_by('created_at')
    elif filter_type == 'popular':
        # Not implemented
        products = products.order_by('-created_at')
    else:
        # Default
        products = products.order_by('-created_at')
    if search_field is not None:
        products = products.filter(Q(name__icontains=search_field) | Q(description__icontains=search_field))

    context = {'products': products}

    return render(request, 'store/home.html', context)


# Product Views
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)
    seller = Seller.objects.get(pk=product.created_by_seller.pk)
    context = {'product': product, 'related_products': related_products, 'seller': seller.user}
    return render(request, 'store/product_detail.html', context)


@seller_required
def add_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            seller = Seller.objects.get(user=request.user)
            product.created_by_seller = seller
            product.save()
            return redirect('home')
        else:
            messages.error(request, 'Invalid New Product')

    return render(request, 'store/add_product_form.html', {'form': form})


@seller_required
def edit_product(request, pk):
    product = Product.objects.get(id=pk)

    seller = Seller.objects.get(user=request.user)

    if not product.created_by_seller == seller:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('home')

    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully updated your product.')
            return redirect('home')
        else:
            messages.error(request, 'Cannot edit Product')

    return render(request, 'store/edit_product_form.html', {'form': form})


def delete_product(request, pk):
    if request.method == "POST":
        product = Product.objects.get(pk=pk)
        product.delete()
    else:
        messages.error(request, "You don't have permission to delete this product!")
    return redirect('home')


@seller_required
def view_created_products(request):
    seller = Seller.objects.get(user=request.user)
    return render(request, "store/view_created_products.html", {'products': seller.all_products.all()})


@login_required(login_url='/login/')
def update_user_profile(request):
    current_user = request.user
    if current_user.is_seller:
        current_user_profile = Seller.objects.get(user=current_user)
        form = SellerForm(request.POST or None, instance=current_user_profile)
    elif current_user.is_customer:
        current_user_profile = Customer.objects.get(user=current_user)
        form = CustomerForm(request.POST or None, instance=current_user_profile)
    else:
        messages.error(request, "You are not a customer or seller")
        return redirect('home')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, 'You have successfully updated your profile.')
            return redirect('home')
        messages.error(request, 'Cannot edit Profile')
    return render(request, 'store/update_user_profile_form.html', {'form': form})


# Category Views
@admin_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        Category.objects.create(name=category_name)
        return redirect('home')

    return render(request, 'store/add_category_form.html')


def list_categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'store/list_categories.html', context)


# Cart views
@customer_required
def add_product_to_cart(request, pk):
    if request.method == 'POST':
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(user=customer)

        product = get_object_or_404(Product, id=pk)

        quantity = int(request.POST.get("productQuantity"))

        cartItem, created = CartItem.objects.get_or_create(cart=cart, productItem=product)
        cartItem.quantity = quantity
        cartItem.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        messages.error(request, 'You do not have permission to add a new product')
        return redirect('home')


@customer_required
def show_cart(request):
    customer = request.user.customer
    cart, _ = Cart.objects.get_or_create(created_by_customer=customer)

    items = cart.items.select_related('productItem').all()
    total = sum(item.productItem.price * item.quantity for item in items)

    return render(request, 'store/show_cart.html', {'cart': cart, 'items': items, 'total': total})


@customer_required
def delete_item(request, pk):
    if request.method == 'POST':
        current_user = request.user
        cart = get_object_or_404(Cart, created_by_customer__user=current_user)
        CartItem.objects.filter(cart=cart, productItem_id=pk).delete()
    else:
        messages.error(request, 'You do not have permission to delete the item!')
    return redirect('show_cart')


# Order views
@customer_required
def checkout_order(request):
    if request.method == "POST":
        customer = request.user.customer
        cart = customer.cart

        order = Order.objects.create(customer=customer)
        items = cart.items.select_related('productItem').all()

        for item in items:
            OrderItem.objects.create(order=order, product=item.productItem, quantity=item.quantity,
                                     price=item.productItem.price)
        cart.delete()
    else:
        messages.error(request, 'You do not have permission to add a new order')
    return redirect('home')


@customer_required
def show_orders(request):
    customer = request.user.customer
    orders = customer.orders.all()
    return render(request, 'store/show_orders.html', {'orders': orders})


@customer_required
def show_order_detail(request, pk):
    order = Order.objects.prefetch_related('items').get(id=pk)
    if order.customer.user != request.user:
        messages.error(request, 'You do not have permission to view this order!')
        return redirect('home')
    total_price = sum(item.price * item.quantity for item in order.items.all())
    context = {'order': order, 'total_price': total_price}
    return render(request, 'store/show_order_detail.html', context)


@admin_required
def show_all_orders(request):
    orders = Order.objects.all()
    return render(request, 'store/show_orders.html', {'orders': orders})


# -----Api Views-----
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsSellerUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListProductSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateProductSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        seller = Seller.objects.get(user=self.request.user)
        if instance.created_by_seller != seller:
            raise serializers.ValidationError("You cannot edit other sellers's products.")

        serializer = CreateProductSerializer(instance, data=request.data, partial=partial,
                                             context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        seller = Seller.objects.get(user=self.request.user)
        if instance.created_by_seller != seller:
            raise serializers.ValidationError("You cannot delete other sellers products.")

        return super().destroy(request, *args, **kwargs)


class CartList(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [IsAdminUser()]

    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        created_by_customer = Customer.objects.get(user=request.user)
        (cart, created) = Cart.objects.get_or_create(created_by_customer=created_by_customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartDetail(APIView):
    permission_classes = [IsCustomerUser]

    def get(self, request):
        created_by_customer = Customer.objects.get(user=request.user)
        cart = get_object_or_404(Cart.objects.prefetch_related("items__productItem"),
                                 created_by_customer=created_by_customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        created_by_customer = Customer.objects.get(user=request.user)
        cart = get_object_or_404(Cart, created_by_customer=created_by_customer)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsCustomerUser]
    queryset = CartItem.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemSerializer
        elif self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UpdateCartItemSerializer

    def get_serializer_context(self):
        created_by_customer = Customer.objects.get(user=self.request.user)
        cart = get_object_or_404(Cart, created_by_customer=created_by_customer)
        if self.request.method == 'POST':
            return {'cart': cart}
        elif self.request.method in ['PUT', 'PATCH']:
            return {'customer': created_by_customer}

    def list(self, request, *args, **kwargs):
        created_by_customer = Customer.objects.get(user=request.user)
        cart = get_object_or_404(Cart, created_by_customer=created_by_customer)
        cart_items = CartItem.objects.select_related('productItem').filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        customer = Customer.objects.get(user=self.request.user)
        cart = get_object_or_404(Cart, items__id=instance.id)
        if cart.created_by_customer != customer:
            raise serializers.ValidationError("You cannot view other customers items.")
        serializer = CartItemSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        customer = Customer.objects.get(user=self.request.user)
        cart = get_object_or_404(Cart, items__id=instance.id)
        if cart.created_by_customer != customer:
            raise serializers.ValidationError("You cannot delete other customers items.")
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    http_method_names = ['get', 'put']

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsCustomerUser])
    def me(self, request):
        customer = Customer.objects.get(user=request.user)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class SellerViewSet(ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put']

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsSellerUser])
    def me(self, request):
        seller = Seller.objects.get(user=request.user)
        if request.method == 'GET':
            serializer = SellerSerializer(seller)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = SellerSerializer(seller, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsCustomerUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        elif self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UpdateOrderSerializer

    def get_serializer_context(self):
        if self.request.method == 'POST':
            return {'user_id': self.request.user.id}

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        customer = Customer.objects.get(user=self.request.user)
        return Order.objects.filter(customer=customer)
