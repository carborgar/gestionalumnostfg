# -*- coding: utf-8 -*-
"""
Django settings for GestionAlumnos project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from .data_properties import *
from .settings_secret import *

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


FILE_CHARSET = 'UTF-8'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'principal',
    'endless_pagination',
    'django.contrib.humanize',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Dir for i18n
LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

ROOT_URLCONF = 'gestionalumnos.urls'

WSGI_APPLICATION = 'gestionalumnos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'gestion',
#         'USER': 'gestionalumnos',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '3306'
#     }
# }

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "/principal/templates"),
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

# --- For transactions -----
ATOMIC_REQUESTS = True

# #LDAP
# AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'django_auth_ldap.backend.LDAPBackend', )
# # Here put the LDAP URL of your server
# AUTH_LDAP_SERVER_URI = 'ldap://ldap.example.com'
# # Let the bind DN and bind password blank for anonymous binding
# AUTH_LDAP_BIND_DN = ""
# AUTH_LDAP_BIND_PASSWORD = ""
# # Lookup user under the branch o=base and by mathcing their uid against the
# # received login name
# AUTH_LDAP_USER_SEARCH = LDAPSearch("o=base",
#     ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'

from django.utils.translation import ugettext_lazy as _

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]
