from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that supports HTTP-only cookie-based tokens.

    Behavior:
        - First checks for JWT in the Authorization header (default behavior)
        - if there is no header, tries to read the token from the "access_token" cookie
        - Validates the access token from the "access_token" cookie

    Use case:
        Enables authentication for applications storing JWTs in cookies
        instead of sending them via Authorization headers.
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        return self.get_user(validated_token), validated_token