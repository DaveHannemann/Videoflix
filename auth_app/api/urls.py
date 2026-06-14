from django.urls import path
from .views import RegistrationView, CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView, ActivateAccountView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('password_reset/', RegistrationView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', RegistrationView.as_view(), name='password_reset_confirm'),
]