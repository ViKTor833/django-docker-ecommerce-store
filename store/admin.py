from django.contrib import admin
from django.utils.html import format_html

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
    list_display = ['name', 'created']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']

    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{url}" width="150" />', url=obj.image.url)
        return "No Image"


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
