from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from store.forms import ChangePasswordForm, SignUpForm, UpdateUserForm, CustomerForm
from store.models import Product, Customer, Seller


# Create your views here.
def home(request):
    products = Product.objects.all()
    context = {'products': products}

    return render(request, 'store/home.html', context)


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)

    context = {'product': product, 'related_products': related_products}
    return render(request, 'store/product_detail.html', context)


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