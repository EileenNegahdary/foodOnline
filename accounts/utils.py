from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings
from .models import User


def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
    elif user.role == 2:
        redirectUrl = 'custDashboard'
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
    return redirectUrl



def send_verification_email(request, user, email_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL

    # to get current site domain address
    current_site = get_current_site(request)
    
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        # encodes primary key of user with base64
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        # generates token for the specific user
        'token': default_token_generator.make_token(user)
    })

    to_email = user.email
    email = EmailMessage(email_subject, message,from_email, to=[to_email])
    email.send()


def send_notification_email(email_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    if(isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    
    email = EmailMessage(email_subject, message, from_email, to=to_email)
    email.send()
    
