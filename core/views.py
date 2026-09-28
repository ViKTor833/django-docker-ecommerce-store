from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from core.forms import SignUpForm, ChangePasswordForm, UpdateUserForm


# Create your views here.
@require_http_methods(["GET", "POST"])
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
                return render(request, 'core/register_form.html', {'form': form})

            user.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'You have successfully registered.')

            return redirect('home')

        messages.error(request, 'Invalid Credentials')

    return render(request, 'core/register_form.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('home')
        messages.error(request, 'Invalid Credentials')

    return render(request, 'core/login_form.html')


@login_required(login_url='login')
@require_POST
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def change_password(request):
    current_user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(current_user, request.POST)
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, 'You have successfully updated your password.')
            return redirect('home')

        messages.error(request, 'Invalid New Password')

    else:
        form = ChangePasswordForm(current_user)

    return render(request, 'core/change_password_form.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def update_user(request):
    current_user = request.user
    form = UpdateUserForm(request.POST or None, instance=current_user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully updated your user account.')
            return redirect('home')
        else:
            messages.error(request, 'Cannot edit user account!')
    return render(request, 'core/update_user_form.html', {'form': form})
