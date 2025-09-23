from django.contrib import admin

from store.models import Customer, Seller, Category, Product, Order, CartItem, Cart, OrderItem


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    list_display = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    list_display = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','created']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']


class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ('customer',)
    list_display = ['id', 'customer', 'placed_at']
    readonly_fields = ['payment_status']
    inlines = [OrderItemInLine]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['created_by_customer__user', 'date_created']
    inlines = [CartItemInline]
