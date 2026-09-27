from django.conf import settings
from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="all_products")

    def __str__(self):
        return f"{self.name} - {self.price}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    placed_at = models.DateTimeField(auto_now_add=True)
    PAYMENT_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed'),
    ]
    payment_status = models.CharField(max_length=1, choices=PAYMENT_CHOICES, default=PAYMENT_CHOICES[0][0])

    def __str__(self):
        return f"{self.customer.user.first_name} {self.customer.user.last_name} {self.payment_status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Cart(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by_customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='cart')

    def __str__(self):
        return f"{self.created_by_customer.user.first_name} - {self.date_created}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    productItem = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.productItem.name} - {self.quantity}"
