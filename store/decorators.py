from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role_attr, login_url='login', redirect_to='home'):
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url=login_url)
        def wrapper(request, *args, **kwargs):
            if not getattr(request.user, role_attr, False):
                messages.error(request, 'You cannot access this page!')
                return redirect(redirect_to)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator



admin_required = role_required('is_admin')
seller_required = role_required('is_seller')
customer_required = role_required('is_customer')
