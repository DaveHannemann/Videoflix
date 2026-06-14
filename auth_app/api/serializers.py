from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles:
        - Password confirmation validation
        - Unique email validation
        - Secure user creation with hashed password
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

        user = User(
            username=validated_data['email'],
            email=validated_data['email'],
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
        - Manually verify email and password
        - Provide consistent error messages
        - Return standard JWT token pair (access + refresh)
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