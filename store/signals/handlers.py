from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Customer, Seller


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_or_seller_after_user(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'C':
            Customer.objects.create(user=instance)
        elif instance.user_type == 'S':
            Seller.objects.create(user=instance)
        elif instance.user_type == 'A':
            Customer.objects.create(user=instance)
            Seller.objects.create(user=instance)
