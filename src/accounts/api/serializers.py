from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=9,
        max_length=20,
        write_only=True,
        error_messages={
            "blank": "Password field may not be blank.",
            "max_length": "Ensure password field has no more than {max_length} characters.",
            "min_length": "Ensure password field has at least {min_length} characters.",
        },
    )

    def validate(self, attrs):
        """Validate password for registration"""
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            name=validated_data["name"], password=validated_data["password"], email=validated_data.get("email", "")
        )

    class Meta:
        model = User
        fields = ("id", "name", "password", "email")


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "name")
        read_only_fields = ("email",)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError("Email is not verified.")
        return data
