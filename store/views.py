from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from store.forms import CustomerForm, ProductForm, SellerForm
from store.models import Product, Customer, Seller, Category, Cart, CartItem, Order, OrderItem
from store.serializers import CategorySerializer, CreateProductSerializer, ListProductSerializer


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
    product = Product.objects.get(pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)
    seller = Seller.objects.get(pk=product.created_by_seller.pk)
    context = {'product': product, 'related_products': related_products, 'seller': seller.user}
    return render(request, 'store/product_detail.html', context)


def add_product(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'S':
        messages.error(request, 'Only available for Seller accounts')
        return redirect('home')

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
            render(request, 'store/add_product_form.html', {'form': form})

    return render(request, 'store/add_product_form.html', {'form': form})


def edit_product(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'S':
        messages.error(request, 'Only available for Seller accounts')
        return redirect('home')

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

    return render(request, 'store/edit_product_form.html', {'form': form})


def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    return redirect('home')


def view_created_products(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'S':
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    seller = Seller.objects.get(user=request.user)
    return render(request, "store/view_created_products.html", {'products': seller.all_products.all()})


def update_user_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    current_user_profile = None
    form = None
    current_user = get_user_model().objects.get(id=request.user.id)
    if current_user.user_type == 'S':
        current_user_profile = Seller.objects.get(user=request.user)
        form = SellerForm(request.POST or None, instance=current_user_profile)
    elif current_user.user_type == 'C':
        current_user_profile = Customer.objects.get(user=request.user)
        form = CustomerForm(request.POST or None, instance=current_user_profile)
    else:
        messages.error(request, "You are not a customer or seller")
        return redirect('home')

    if form.is_valid():
        form.save()
        login(request, current_user)
        messages.success(request, 'You have successfully updated your profile.')
        return redirect('home')
    return render(request, 'store/update_user_profile_form.html', {'form': form})


# Category Views

def add_category(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'A':
        messages.error(request, 'You do not have permission to add a new category')
        return redirect('home')

    if request.method == 'POST':
        category_name = request.POST['category_name']
        Category.objects.create(name=category_name)
        return redirect('home')
    elif request.method == 'GET':
        return render(request, 'store/add_category_form.html')


def list_categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'store/list_categories.html', context)


# Cart views
def add_product_to_cart(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    if not request.user.user_type == 'C':
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        if not Cart.objects.filter(created_by_customer=customer).exists():
            Cart.objects.create(created_by_customer=customer)

        product = Product.objects.get(id=pk)

        quantity = request.POST.get("productQuantity")
        cartItem, created = CartItem.objects.get_or_create(cart=customer.cart, productItem=product)
        cartItem.quantity = int(quantity)
        cartItem.save()
        return redirect('home')
    else:
        messages.error(request, 'You do not have permission to add a new product')
        return redirect('home')


def show_cart(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    if not request.user.user_type == 'C':
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    customer = Customer.objects.get(user=request.user)
    if not Cart.objects.filter(created_by_customer=customer).exists():
        Cart.objects.create(created_by_customer=customer)

    cart = Cart.objects.get(created_by_customer=customer)
    items = cart.items.all()
    total = 0
    for item in items:
        total += item.productItem.price

    return render(request, 'store/show_cart.html', {'cart': cart, 'items': items, 'total': total})


def delete_item(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    customer = Customer.objects.get(user=request.user)
    cart = Cart.objects.get(created_by_customer=customer)
    CartItem.objects.get(cart=cart, productItem=Product.objects.get(pk=pk)).delete()
    return redirect('show_cart')


# Order views
def checkout_order(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    if not request.user.user_type == 'C':
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    customer = Customer.objects.get(user=request.user)
    cart = Cart.objects.get(created_by_customer=customer)

    order = Order.objects.create(customer=customer)
    items = cart.items.all()

    for item in items:
        OrderItem.objects.create(order=order, product=item.productItem, quantity=item.quantity,
                                 price=item.productItem.price)

    cart.delete()
    return redirect('home')


def show_orders(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'C':
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    customer = Customer.objects.get(user=request.user)
    orders = customer.orders.all()
    return render(request, 'store/show_orders.html', {'orders': orders})


def show_order_detail(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not (request.user.user_type == 'C' or request.user.user_type == 'A'):
        messages.error(request, 'Only available for Customer accounts')
        return redirect('home')

    order = Order.objects.prefetch_related('items').get(id=pk)
    total_price = 0
    for item in order.items.all():
        total_price += item.price * item.quantity

    context = {'order': order, 'total_price': total_price}
    return render(request, 'store/show_order_detail.html', context)


def show_all_orders(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')
    if not request.user.user_type == 'A':
        messages.error(request, 'Only available for Admin accounts')
        return redirect('home')
    orders = Order.objects.all()
    return render(request, 'store/show_orders.html', {'orders': orders})


# Api Views

class CategoryList(APIView):
    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(Category, id=pk)
        serializer = CategorySerializer(queryset)
        return Response(serializer.data)

    def delete(self, request, pk):
        queryset = get_object_or_404(Category, id=pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductList(APIView):
    def get(self, request):
        queryset = Product.objects.all()
        serializer = ListProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(Product, id=pk)
        serializer = ListProductSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = get_object_or_404(Product, id=pk)
        serializer = CreateProductSerializer(data=request.data, instance=queryset)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        queryset = get_object_or_404(Product, id=pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
