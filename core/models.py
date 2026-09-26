from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserType(models.TextChoices):
    CUSTOMER = "C", _("Customer")
    SELLER = "S", _("Seller")
    ADMIN = "A", _("Admin")


class User(AbstractUser):
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=1, choices=UserType, default=UserType.CUSTOMER)

    @property
    def is_admin(self):
        return self.user_type == UserType.ADMIN

    @property
    def is_customer(self):
        return self.user_type in [UserType.CUSTOMER, UserType.ADMIN]

    @property
    def is_seller(self):
        return self.user_type in [UserType.SELLER, UserType.ADMIN]
