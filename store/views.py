from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect

from store.forms import ChangePasswordForm, SignUpForm, UpdateUserForm, CustomerForm, ProductForm
from store.models import Product, Customer, Seller, Category


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


# Authentication
def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            userType = request.POST.get('userType')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = form.save(commit=False)
            if userType == 'Customer':
                user.user_type = 'C'
            elif userType == 'Seller':
                user.user_type = 'S'
            else:
                messages.error(request, 'Please select the type of user')
                return render(request, 'store/register_form.html', {'form': form})

            user.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)
            if userType == 'Customer':
                Customer.objects.create(user=request.user)
                messages.success(request, 'Customer Account created successfully')
            elif userType == 'Seller':
                Seller.objects.create(user=request.user)
                messages.success(request, 'Seller Account created successfully')

            return redirect('home')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('register')
    return render(request, 'store/register_form.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'store/login_form.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def change_password(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    current_user = get_user_model().objects.get(id=request.user.id)
    if request.method == 'POST':
        form = ChangePasswordForm(current_user, request.POST)
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, 'You have successfully updated your password.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid New Password')
            return redirect('change_password')
    else:
        form = ChangePasswordForm(current_user)

    return render(request, 'store/change_password_form.html', {'form': form})


def update_user(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    current_user = get_user_model().objects.get(id=request.user.id)
    form = UpdateUserForm(request.POST or None, instance=current_user)

    if form.is_valid():
        form.save()
        login(request, current_user)
        messages.success(request, 'You have successfully updated your user account.')
        return redirect('home')
    return render(request, 'store/update_user_form.html', {'form': form})


def update_user_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to do that.')
        return redirect('login')

    current_user_profile = None
    current_user = get_user_model().objects.get(id=request.user.id)
    if current_user.user_type == 'S':
        current_user_profile = Seller.objects.get(user=request.user)
    elif current_user.user_type == 'C':
        current_user_profile = Customer.objects.get(user=request.user)
    else:
        messages.error(request, "You are not a customer or seller")
        return redirect('home')
    form = CustomerForm(request.POST or None, instance=current_user_profile)

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
