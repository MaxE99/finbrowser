import os
import environ

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG_MODE", False)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
TWEET_IMG_FILE_DIRECTORY = "static/home/tweet_imgs"
INITIAL_TWEET_IMG_FILE_DIRECTORY = "static/home/initial_tweet_imgs"
FAVICON_FILE_DIRECTORY = "static/home/favicons"

if DEBUG:
    ALLOWED_HOSTS = []

    STATIC_URL = "/static/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "uploads/")
    MEDIA_URL = "/uploads/"

else:
    S3_BUCKET = os.environ.get("S3_BUCKET")

    ALLOWED_HOSTS = ["finbrowser.io"]

    # HTTPS Settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_REFERRER_POLICY = "strict-origin"

    # HSTS Settings
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # CSP Settings
    CSP_DEFAULT_SRC = (
        "'self'",
        S3_BUCKET,
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
        "*.google-analytics.com",
        "*.analytics.google.com",
    )
    CSP_STYLE_SRC = (
        "'self'",
        S3_BUCKET,
    )
    CSP_SCRIPT_SRC = (
        "'self'",
        S3_BUCKET,
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
        "*.google-analytics.com",
        "*.analytics.google.com",
    )
    CSP_FONT_SRC = (
        "'self'",
        S3_BUCKET,
    )
    CSP_IMG_SRC = (
        "'self'",
        S3_BUCKET,
    )
    CSP_CONNECT_SRC = (
        "'self'",
        S3_BUCKET,
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
        "*.google-analytics.com",
        "*.analytics.google.com",
    )
    CSP_INCLUDE_NONCE_IN = ["script-src"]

    # AWS Settings
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = "finbrowser-assets"
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.us-east-2.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_LOCATION = "static"
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "researchbrowserproject.storages.MediaStore"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_MASTER_PASSWORD"),
        "HOST": os.environ.get("DB_HOSTNAME"),
        "PORT": "5432",
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "django_filters",
    "rest_framework",
    "django.contrib.sitemaps",
    # 'debug_toolbar',
    "django_cleanup.apps.CleanupConfig",
    "apps.accounts",
    "apps.home",
    "apps.registration",
    "apps.source",
    "apps.support",
    "apps.sector",
    "apps.list",
    "apps.article",
    "apps.stock",
    "apps.tasks",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

AUTH_USER_MODEL = "accounts.User"

SITE_ID = 2

MIDDLEWARE = [
    "researchbrowserproject.middleware.health_check_middleware.AliveCheck",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "researchbrowserproject.middleware.timezone_middleware.TimezoneMiddleware",
]

ROOT_URLCONF = "researchbrowserproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "researchbrowserproject.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ACCOUNT_FORMS = {"signup": "apps.registration.forms.CustomSignUpForm"}

LOGIN_URL = "/registration/login/"

LOGIN_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PW")
EMAIL_USE_TLS = True

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Deactivates Browsable API
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# needed for django debug_toolbar
# INTERNAL_IPS = [
#     "127.0.0.1",
# ]
