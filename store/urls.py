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

    path("products/", views.view_created_products, name="product_list"),
    path('product/add/', views.add_product, name='product_add'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.edit_product, name='product_edit'),
    path('product/<int:pk>/delete/', views.delete_product, name='product_delete'),

    path('category/add/', views.add_category, name='category_add'),
    path('categories/', views.list_categories, name='category_list'),

    path('cart/', views.show_cart, name='cart_detail'),
    path('cart/add/<int:pk>/', views.add_product_to_cart, name='cart_add_item'),
    path('cart/remove/<int:pk>/', views.delete_item, name='cart_remove_item'),

    path('order/checkout/', views.checkout_order, name='order_checkout'),
    path('order/<int:pk>/', views.show_order_detail, name='order_detail'),
    path('orders/all/', views.show_all_orders, name='orders_all'),
    path('orders/my/', views.show_my_orders, name='orders_my'),

    path('profile/', views.update_user_profile, name='profile_detail'),
    # ---API-Paths---
    path('api/', include(router.urls)),
    path('api/carts/', views.AdminCartList.as_view()),
    path('api/carts/mycart/', views.CustomerCartView.as_view()),
    path('api/carts/mycart/', include(router2.urls)),
]
