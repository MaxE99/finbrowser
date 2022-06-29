# Python Imports
import os
import environ

env = environ.Env()
environ.Env.read_env()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEBUG = False
if DEBUG:
    ALLOWED_HOSTS = []
    STATIC_URL = '/static/'
    SECRET_KEY = env('SECRET_KEY')
    # MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads/')
    # MEDIA_URL = '/uploads/'
    FAVICON_FILE_DIRECTORY =  os.path.join(BASE_DIR, 'apps/home/static/home/favicons')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'testdb',
            'USER': 'postgres',
            'PASSWORD': 'post123gres',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
else:
    SECRET_KEY =  os.environ.get('SECRET_KEY')
    ALLOWED_HOSTS = ['researchbrowser.herokuapp.com', 'finbrowser.io']
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = 'django-testbucket24061436'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.us-east-2.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_LOCATION = 'static'
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = "researchbrowserproject.storages.MediaStore"
    FAVICON_LOCATION = 'static/home/favicons'
    FAVICON_FILE_DIRECTORY = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, FAVICON_LOCATION)
    # HTTPS Settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = "strict-origin"
    # HSTS Settings
    SECURE_HSTS_SECONDS = 60 # Wert erhöhen wenn Tests erfolgreich sind
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DATABASE_NAME'),
            'USER': os.environ.get('DATABASE_USER'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
            'HOST': os.environ.get('DATABASE_HOST'),
            'PORT': '5432',
        }
    }


# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
#     # os.path.join(BASE_DIR, 'home/static/home/favicons')
# ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_filters',
    'rest_framework',
    'django.contrib.sitemaps',
    'django_celery_beat',
    # 'debug_toolbar',
    'django_cleanup.apps.CleanupConfig',
    'apps.accounts',
    'apps.home',
    'apps.registration',
    'apps.source',
    'apps.support',
    'apps.sector',
    'apps.list',
    'apps.article',
    'apps.scrapper',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

AUTH_USER_MODEL = 'accounts.User'

SITE_ID = 2

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'researchbrowserproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'researchbrowserproject.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ACCOUNT_FORMS = {'signup': 'apps.registration.forms.CustomSignUpForm'}

LOGIN_URL = '/registration/login/'

LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework.authentication.SessionAuthentication',
    )
}

# Only for django debug_toolbar
# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]




