from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def send_activation_email(user, activation_link):
    context = {
        "username": user.username,
        "activation_link": activation_link,
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

    email.send()