# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
import hashlib


def send_email_create_user(user, password, request):
    mail_sting = render_to_string('email/register.html', {'user': user, 'password': password, 'request': request})
    send_mail([user.email], 'Bienvenido / Welcome', mail_sting)


def send_tutorial_request_mail(request, tutorial_request):
    accept_from_mail_token = hashlib.sha512(str(tutorial_request.activation_hash).encode('utf-8')).hexdigest()
    mail_sting = render_to_string('email/lecturer_tutorial_request.html',
                                  {'tutorial_request': tutorial_request, 'token': accept_from_mail_token,
                                   'request': request})
    send_mail([tutorial_request.profesor.email], 'Petición recibida / Request received', mail_sting)


def send_tutorial_accepted_mail(tutorial_request):
    mail_sting = render_to_string('email/student_request_accepted.html', {'tutorial_request': tutorial_request})
    send_mail([tutorial_request.profesor.email], 'Petición aceptada / Accepted request', mail_sting)


def send_tutorial_rejected_mail(tutorial_request):
    mail_sting = render_to_string('email/student_request_rejected.html', {'tutorial_request': tutorial_request})
    send_mail([tutorial_request.profesor.email], 'Petición rechazada / Request rejected', mail_sting)


def send_mail(to_list, subject, content):
    email = EmailMessage(subject, content, to=[to for to in to_list])
    email.content_subtype = 'html'
    email.send(fail_silently=True)
