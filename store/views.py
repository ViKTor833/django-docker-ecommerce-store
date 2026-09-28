from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from rest_framework import status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser
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
@require_GET
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
@require_GET
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'created_by_seller__user'), pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)
    context = {'product': product, 'related_products': related_products, 'seller': product.created_by_seller.user}
    return render(request, 'store/product_detail.html', context)


@seller_required
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET", "POST"])
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


@require_POST
def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    return redirect('home')


@seller_required
@require_GET
def view_created_products(request):
    seller = request.user.seller
    products = seller.all_products.select_related('category').all()
    return render(request, "store/view_created_products.html", {'products': products})


@login_required(login_url='/login/')
@require_http_methods(["GET", "POST"])
def update_user_profile(request):
    current_user = request.user
    customer_form = None
    seller_form = None
    form = None
    if current_user.is_admin:
        customer_profile = Customer.objects.get(user=current_user)
        seller_profile = Seller.objects.get(user=current_user)
        customer_form = CustomerForm(request.POST or None, instance=customer_profile)
        seller_form = SellerForm(request.POST or None, instance=seller_profile)
    elif current_user.is_seller:
        seller_profile = Seller.objects.get(user=current_user)
        form = SellerForm(request.POST or None, instance=seller_profile)
    elif current_user.is_customer:
        customer_form = Customer.objects.get(user=current_user)
        form = CustomerForm(request.POST or None, instance=customer_form)

    if request.method == 'POST':
        if current_user.is_admin:
            if customer_form.is_valid() and seller_form.is_valid():
                customer_form.save()
                seller_form.save()
                messages.success(request, 'You have successfully updated your profile.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid form data.')
        else:
            if form.is_valid():
                form.save()
                messages.success(request, 'You have successfully updated your profile.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid form data.')
    context = {
        'customer_form': customer_form,
        'seller_form': seller_form,
        'form': form,
    }
    return render(request, 'store/update_user_profile_form.html', context)


# Category Views
@admin_required
@require_http_methods(["GET", "POST"])
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        Category.objects.create(name=category_name)
        return redirect('home')

    return render(request, 'store/add_category_form.html')


@require_GET
def list_categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'store/list_categories.html', context)


# Cart views
@customer_required
@require_POST
def add_product_to_cart(request, pk):
    customer = request.user.customer
    cart, created = Cart.objects.get_or_create(created_by_customer=customer)
    product = get_object_or_404(Product, id=pk)
    quantity = int(request.POST.get("productQuantity", 1))
    cartItem, created = CartItem.objects.get_or_create(cart=cart, productItem=product)
    cartItem.quantity = quantity
    cartItem.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


@customer_required
@require_GET
def show_cart(request):
    customer = request.user.customer
    cart, _ = Cart.objects.get_or_create(created_by_customer=customer)

    items = cart.items.select_related('productItem__category').all()
    total = sum(item.productItem.price * item.quantity for item in items)

    return render(request, 'store/show_cart.html', {'cart': cart, 'items': items, 'total': total})


@customer_required
@require_POST
def delete_item(request, pk):
    current_user = request.user
    cart = get_object_or_404(Cart, created_by_customer__user=current_user)
    CartItem.objects.filter(cart=cart, productItem_id=pk).delete()
    return redirect('show_cart')


# Order views
@customer_required
@require_POST
def checkout_order(request):
    customer = request.user.customer
    cart = customer.cart
    with transaction.atomic():
        order = Order.objects.create(customer=customer)
        items = cart.items.select_related('productItem').all()

        for item in items:
            OrderItem.objects.create(order=order, product=item.productItem, quantity=item.quantity,
                                     price=item.productItem.price, product_name=item.productItem.name)
        cart.delete()

    return redirect('home')


@customer_required
@require_GET
def show_orders(request):
    customer = request.user.customer
    orders = customer.orders.select_related('customer__user').all()
    return render(request, 'store/show_orders.html', {'orders': orders})


@customer_required
@require_GET
def show_order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('customer__user').prefetch_related('items'), id=pk)

    if order.customer.user != request.user:
        messages.error(request, 'You do not have permission to view this order!')
        return redirect('home')
    total_price = sum(item.price * item.quantity for item in order.items.all())
    context = {'order': order, 'total_price': total_price}
    return render(request, 'store/show_order_detail.html', context)


@admin_required
@require_GET
def show_all_orders(request):
    orders = Order.objects.select_related('customer__user').all()
    return render(request, 'store/show_orders.html', {'orders': orders})


# -----Api Views-----
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('category', 'created_by_seller__user').all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsSellerUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListProductSerializer
        return CreateProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['user_id'] = self.request.user.id
        return context

    def perform_update(self, serializer):
        seller = Seller.objects.get(user=self.request.user)
        instance = self.get_object()
        if instance.created_by_seller != seller:
            raise serializers.ValidationError("You cannot edit other sellers' products")
        serializer.save()

    def perform_destroy(self, instance):
        seller = Seller.objects.get(user=self.request.user)
        if instance.created_by_seller != seller:
            raise serializers.ValidationError("You cannot delete other sellers' products")
        instance.delete()


class AdminCartList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        carts = Cart.objects.select_related("created_by_customer__user").prefetch_related("items__productItem").all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)


class CustomerCartView(APIView):
    permission_classes = [IsCustomerUser]

    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        cart, created = Cart.objects.prefetch_related("items__productItem").get_or_create(created_by_customer=customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        customer = Customer.objects.get(user=request.user)
        cart = get_object_or_404(Cart, created_by_customer=customer)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        customer = Customer.objects.get(user=self.request.user)
        return CartItem.objects.select_related("productItem").filter(cart__created_by_customer=customer)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == "POST":
            customer = Customer.objects.get(user=self.request.user)
            cart, created = Cart.objects.get_or_create(created_by_customer=customer)
            context['cart'] = cart

        return context


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    http_method_names = ['get', 'put', 'patch']

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], permission_classes=[IsCustomerUser])
    def me(self, request):
        customer = Customer.objects.get(user=request.user)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        partial = request.method == 'PATCH'
        serializer = CustomerSerializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SellerViewSet(ModelViewSet):
    queryset = Seller.objects.select_related('user').all()
    serializer_class = SellerSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put', 'patch']

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], permission_classes=[IsSellerUser])
    def me(self, request):
        seller = Seller.objects.get(user=request.user)
        if request.method == 'GET':
            serializer = SellerSerializer(seller)
            return Response(serializer.data)

        partial = request.method == 'PATCH'
        serializer = SellerSerializer(seller, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAdminUser()]
        return [IsCustomerUser()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UpdateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'POST':
            context['user_id'] = self.request.user.id
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related("customer__user").prefetch_related("items__productItem")

        if user.is_staff or user.is_admin:
            return queryset.all()

        customer = Customer.objects.get(user=user)
        return queryset.filter(customer=customer)
