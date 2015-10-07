# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _

username_validator = RegexValidator(
    r'^\d{8}[a-zA-Z]$',
    message=_('It uses a format that matches the requested, ') + "00000000A"
)
