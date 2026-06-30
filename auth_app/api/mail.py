"""
Utility functions for sending transactional emails.

Provides helpers for:
    - Account activation emails
    - Password reset emails
"""

from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from pathlib import Path

def send_activation_email(user, activation_link, token, uidb64):
    """
    Sends the account activation email.

    Renders both plain text and HTML email templates and
    delivers an activation email containing the unique
    activation link for the newly registered user.
    """

    context = {
        "username": user.username,
        "activation_link": activation_link,
        "token": token,
        "uidb64": uidb64
    }

    text_content = render_to_string(
        "emails/activation.txt",
        context
    )

    html_content = render_to_string(
        "emails/activation.html",
        context
    )

    email = EmailMultiAlternatives(
        subject="Activate your Videoflix account",
        body=text_content,
        to=[user.email]
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    logo_path = Path(settings.BASE_DIR) / "assets" / "images" / "LogoVideoFlix.png"

    with open(logo_path, "rb") as f:
        logo = MIMEImage(f.read())
        logo.add_header("Content-ID", "<videoflix-logo>")
        logo.add_header("Content-Disposition", "inline", filename="LogoVideoFlix.png")

    email.attach(logo)

    email.send()

def send_password_reset_email(user, reset_link):
    """
    Sends the password reset email.

    Renders both plain text and HTML email templates and
    delivers a password reset link to the user's email address.
    """
        
    context = {
        "username": user.username,
        "reset_link": reset_link,
    }

    text_content = render_to_string(
        "emails/password.txt",
        context
    )

    html_content = render_to_string(
        "emails/password.html",
        context
    )

    email = EmailMultiAlternatives(
        subject="Reset your Videoflix password",
        body=text_content,
        to=[user.email]
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    logo_path = Path(settings.BASE_DIR) / "assets" / "images" / "LogoVideoFlix.png"

    with open(logo_path, "rb") as f:
        logo = MIMEImage(f.read())
        logo.add_header("Content-ID", "<videoflix-logo>")
        logo.add_header("Content-Disposition", "inline", filename="LogoVideoFlix.png")

    email.attach(logo)

    email.send()