from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('customers', views.CustomerViewSet)
router.register('sellers', views.SellerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

router2 = DefaultRouter()
router2.register('items', views.CartItemViewSet, basename='items')

urlpatterns = [
    path('', views.home, name='home'),

    path("products/", views.product_list, name="product_list"),
    path('product/add/', views.product_add, name='product_add'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('category/add/', views.category_add, name='category_add'),
    path('categories/', views.category_list, name='category_list'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:pk>/', views.cart_add_item, name='cart_add_item'),
    path('cart/remove/<int:pk>/', views.cart_remove_item, name='cart_remove_item'),

    path('order/checkout/', views.order_checkout, name='order_checkout'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/all/', views.orders_all, name='orders_all'),
    path('orders/my/', views.orders_my, name='orders_my'),

    path('profile/', views.profile_detail, name='profile_detail'),
    # ---API-Paths---
    path('api/', include(router.urls)),
    path('api/carts/', views.AdminCartList.as_view()),
    path('api/carts/mycart/', views.CustomerCartView.as_view()),
    path('api/carts/mycart/', include(router2.urls)),
]
