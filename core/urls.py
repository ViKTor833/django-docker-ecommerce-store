from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('user/update/', views.update_user, name='user_update'),
    path('user/password/change/', views.change_password, name='user_password_change'),
]
