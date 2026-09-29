from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('user/update/', views.user_update, name='user_update'),
    path('user/password/change/', views.user_password_change, name='user_password_change'),
]
