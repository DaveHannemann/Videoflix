from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.authentication import CookieJWTAuthentication
from .serializers import CustomTokenObtainPairSerializer, PasswordResetSerializer, RegistrationSerializer, PasswordResetConfirmSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .utils import set_access_cookie, set_refresh_cookie, delete_auth_cookies
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from .mail import send_activation_email, send_password_reset_email

User = get_user_model()

class RegistrationView(APIView):
    """
    Handles user registration.

    Accepts user data (e.g email, password),
    validates it via RegistrationSerializer.

    Creates a new inactive user account and sends an
    email containing an activation link.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)


        if serializer.is_valid():
            user = serializer.save()
                
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            activation_token = default_token_generator.make_token(user)

            activation_link = (f"http://localhost:5500/pages/auth/activate.html?uid={uidb64}&token={activation_token}")

            send_activation_email(
                user=user,
                activation_link=activation_link,
                token=activation_token,
                uidb64=uidb64
            )

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "uidb64": uidb64,
                "activation_token": activation_token,
                "activation_link": activation_link
            }, status=status.HTTP_201_CREATED)

            # return Response({'detail': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Authenticates a user and issues JWT tokens via HTTP-only cookies.

    Overrides the default TokenObtainPairView to:
        - Return user information
        - Store access and refresh tokens in cookies instead of response body

    Cookies:
        - access_token (short-lived)
        - refresh_token (long-lived)
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        data = {}
        if serializer.is_valid():
            data = {
                'id': serializer.user.id,
                'username': serializer.user.username,
            }

            refresh = serializer.validated_data["refresh"]
            access = serializer.validated_data["access"]

            response = Response({"detail": "Login successfully!", 'user': data})

            set_access_cookie(response, access)
            set_refresh_cookie(response, refresh)

            return response
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        

class LogoutView(APIView):
    """
    Logs out the authenticated user.

    Invalidates the refresh token by adding it to the blacklist
    and removes both JWT authentication cookies from the client.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass
            
        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."})
        delete_auth_cookies(response)
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    """
    Refreshes the access token using the refresh token stored in cookies.

    Overrides the default TokenRefreshView to:
        - Read refresh token from HTTP-only cookie
        - Generate a new access token and update cookie

    Cookies:
        - refresh_token (read)
        - access_token (updated)
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "Refresh token not provided or missing"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"detail": "Refresh token not provided or missing"}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get("access")

        response = Response({"detail": "Token refreshed successfully!"})
        set_access_cookie(response, access_token)

        return response
    
class ActivateAccountView(APIView):
    """
    Activates a newly registered user account.

    Validates the UID and activation token received via the
    activation link sent by email. If both are valid, the user
    account is activated by setting `is_active=True`.

    URL Parameters:
        - uidb64: Base64 encoded user ID
        - token: Django activation token
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid activation link"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return Response(
                {"detail": "Account successfully activated."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid or expired token"},
            status=status.HTTP_400_BAD_REQUEST
        )

class PasswordResetView(APIView):
    """
    Sends a password reset email.

    Accepts an email address and, if a matching user exists,
    generates a password reset token and sends a reset link.

    For security reasons, the same success response is returned
    regardless of whether the email address exists.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(
        data=request.data
    )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'An email has been sent to reset your password.'}, status=status.HTTP_200_OK)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = (f"http://localhost:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}")

        send_password_reset_email(
            user=user,
            reset_link=reset_link
        )

        return Response({'detail': 'An email has been sent to reset your password.'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(APIView):
    """
    Resets a user's password.

    Validates the password reset token and updates the user's
    password if the provided token is valid.

    URL Parameters:
        - uidb64: Base64 encoded user ID
        - token: Django password reset token
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Invalid password reset link'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)