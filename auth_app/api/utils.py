import re

from django.contrib.auth import get_user_model

User = get_user_model()

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": True,
    "samesite": "Lax",
}


def set_access_cookie(response, token):
    response.set_cookie(
        key="access_token",
        value=str(token),
        **COOKIE_SETTINGS
    )


def set_refresh_cookie(response, token):
    response.set_cookie(
        key="refresh_token",
        value=str(token),
        **COOKIE_SETTINGS
    )


def delete_auth_cookies(response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def generate_username(email):
    local_part = email.split('@')[0]
    base = local_part.split('.')[0].lower()

    base = re.sub(r'[^a-z0-9]', '', base)

    username = base
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1

    return username