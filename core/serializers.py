from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    USER_CHOICES = {
        ("C", "Customer"),
        ("S", "Seller")
    }
    user_type = serializers.ChoiceField(choices=USER_CHOICES)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'user_type']
