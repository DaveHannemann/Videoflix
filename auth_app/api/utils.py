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