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
router2.register('items', views.CartItemViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>', views.product_detail, name='product_detail'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>', views.delete_product, name='delete_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('list_categories/', views.list_categories, name='list_categories'),
    path('add_product_to_cart/<int:pk>', views.add_product_to_cart, name='add_product_to_cart'),
    path('show_cart/', views.show_cart, name='show_cart'),
    path('delete_item/<int:pk>', views.delete_item, name='delete_item_from_cart'),
    path('checkout_order/', views.checkout_order, name='checkout_order'),
    path('show_orders/', views.show_orders, name='show_orders'),
    path('show_order/<int:pk>', views.show_order_detail, name='show_order_detail'),
    path("view_created_products/", views.view_created_products, name="view_created_products"),
    path('show_all_orders/', views.show_all_orders, name='show_all_orders'),

    # ---API-Paths---
    path('api/', include(router.urls)),
    path('api/carts/', views.AdminCartList.as_view()),
    path('api/carts/mycart/', views.CustomerCartView.as_view()),
    path('api/carts/mycart/', include(router2.urls)),
]
