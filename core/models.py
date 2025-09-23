from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USER_TYPE = [
        ('A', 'Admin'),
        ('C', 'Customer'),
        ('S', 'Seller'),
    ]

    user_type = models.CharField(max_length=1, choices=USER_TYPE, default=USER_TYPE[1][0])
