"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-drw6!*s_ril1+bg*2y)0)sl7y#g_7s1uev$p1m$ce=xu7ahf3%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', default=0))
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'snf-21517.ok-kno.grnetcloud.net', 'snf-21427.ok-kno.grnetcloud.net']
APPEND_SLASH = True

API_PREFIX = 'api/v1'

# SSI configuration
WALTDIR = os.environ.get('WALTDIR')
APPDIR = os.environ.get('APPDIR')
STORAGE = os.environ.get('STORAGE')
TMPDIR = os.environ.get('TMPDIR')
EBSI_PRFX = 'did:ebsi:'


# Login
UI_TOKEN_LOGIN_URL = '/login/code/#%s'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + [
    'core.apps.CoreConfig',
    'oauth.apps.OauthConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_project.wsgi.application'

# Oauth

PN_GOOGLE = 'google'

AUTHLIB_OAUTH_CLIENTS = {
    PN_GOOGLE: {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        'access_token_url': os.environ.get('GOOGLE_TOKEN_URL', ''),
        'authorize_url': os.environ.get('GOOGLE_AUTHORIZE_URL', ''),
        'api_base_url': os.environ.get('GOOGLE_API_BASE_URL', ''),
        'server_metadata_url': os.environ.get(
            'GOOGLE_SERVER_METADATA_URL', None
        ),
        'client_kwargs': {
            'scope': os.environ.get(
                'GOOGLE_SCOPE', 'openid profile email'
            ),
        }
    },
    # Put here further oauth clients
    # ...
}

AUTH_STATE_PREFIX = os.environ.get('AUTH_STATE_PREFIX', default='')

CODE_EXPIRES_AFTER_SECS = int(os.environ.get(
    'EBSI_DIPLOMAS_CODE_EXPIRES_AFTER_SECS', 3600))
TOKEN_EXPIRES_AFTER_SECS = 3600 * 24 * 365 if DEBUG else int(os.environ.get(
    'EBSI_DIPLOMAS_TOKEN_EXPIRES_AFTER_SECS', 20 * 60))
TOKEN_REFRESH_AFTER_SECS = int(os.environ.get(
    'EBSI_DIPLOMAS_API_TOKEN_REFRESH_AFTER_SECS', 2 * 60))

# Cache

CACHE_HOST = os.environ.get('CACHE_HOST', 'localhost')
CACHE_PORT = os.environ.get('CACHE_PORT', '11211')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': f'{CACHE_HOST}:{CACHE_PORT}',
    }
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',           # TODO
    },
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
