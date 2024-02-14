import os
from pathlib import Path
import environ


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = ['rnrrooms.aamarpay.dev', '127.0.0.1']

# CSRF trusted origin
CSRF_TRUSTED_ORIGINS = ['https://rnrrooms.aamarpay.dev']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rnr.apps.RNRConfig',
    'payment.apps.PaymentConfig',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
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

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASS"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

RNR_HOSTNAME = "beta.api.rnrrooms.com"

RNR_HOSTNAME = env("RNR_HOSTNAME")
RNR_BASE_URL = "https://{}".format(RNR_HOSTNAME)
RNR_API_KEY = env("RNR_API_KEY")
RNR_API_SECRET_KEY = env("RNR_API_SECRET_KEY")
RNR_USERNAME = env("RNR_USERNAME")
RNR_PASSWORD = env("RNR_PASSWORD")

AAMARPAY_DEV_URL = "http://sandbox.aamarpay.com/"

AAMARPAY_DEV_URL = env("AAMARPAY_DEV_URL")
AAMARPAY_STORE_ID = env("AAMARPAY_STORE_ID")
AAMARPAY_SIGNATURE_KEY = env("AAMARPAY_SIGNATURE_KEY")


SPECTACULAR_SETTINGS = {
    'TITLE': 'RnR Room',
    'DESCRIPTION': 'RnR Room',
    'VERSION': '1.0.0',
}
