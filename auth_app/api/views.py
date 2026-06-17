from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.authentication import CookieJWTAuthentication
from .serializers import CustomTokenObtainPairSerializer, RegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .utils import set_access_cookie, set_refresh_cookie, delete_auth_cookies
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from .mail import send_activation_email

User = get_user_model()

class RegistrationView(APIView):
    """
    Handles user registration.

    Accepts user data (e.g email, password),
    validates it via RegistrationSerializer, and creates a new user.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)


        if serializer.is_valid():
            user = serializer.save()
                
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            token = default_token_generator.make_token(user)

            activation_link = (f"http://localhost:8000/api/activate/"f"{uidb64}/{token}/")

            send_activation_email(
                user=user,
                activation_link=activation_link
            )

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
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
    Logs out the authenticated user by removing JWT cookies.
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