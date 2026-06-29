from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

from auth_app.api.utils import generate_username

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles:
        - Password confirmation validation
        - Unique email validation
        - Secure user creation with hashed password
        - Newly created accounts are inactive until activated
    """
    
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        validated_data.pop('confirmed_password')

        email = validated_data['email']
        username = generate_username(email)

        user = User(
            username=username,
            email=email,
            is_active=False
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    

User = get_user_model()

class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Custom JWT serializer for user authentication.

    Overrides default validation to:
        - Authenticate users via email instead of username
        - Verify account activation
        - Provide consistent authentication error messages
        - Return a JWT access and refresh token pair
    """

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.is_active:
            raise serializers.ValidationError('Account is not activated')

        refresh = RefreshToken.for_user(user)

        self.user = user

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    

class PasswordResetSerializer(serializers.Serializer):
    """
    Validates the email address used for requesting
    a password reset.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Validates the new password during the password reset process.

    Ensures that:
        - Both password fields match
        - The password satisfies Django's password validators
    """
        
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                "Passwords do not match"
            )

        validate_password(attrs["new_password"])

        return attrs