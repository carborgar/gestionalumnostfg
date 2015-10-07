# -*- coding: utf-8 -*-

from django.contrib import messages
from django.utils.translation import ugettext as _
import random
import string
from django.utils.crypto import get_random_string


def secret_key():
    return get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')


def id_generator(size=5, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    number = random.choice(string.digits)
    lower = random.choice(string.ascii_lowercase)
    upper = random.choice(string.ascii_uppercase)
    password = number + lower + upper
    password += ''.join(random.choice(chars) for _ in range(size))
    return password



