from pathlib import Path
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

DB = os.getenv('DB')

ALLOWED_HOSTS = [
        'localhost',
        '0.0.0.0',
        'webserver',
        '127.0.0.1',
    ]

if DB == 'lite':

    ALLOWED_HOSTS.append('.ngrok-free.app')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

elif DB == 'postgres':

    hosts = ['45.9.43.22', '.broteamracing.ru']
    ALLOWED_HOSTS.extend(hosts)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': 5432,
        }
    }

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'btr.auth',
    'btr.users.apps.UsersConfig',
    'btr.bookings.apps.BookingsConfig',
    'btr.workhours.apps.WorkHoursConfig',
    'btr',
    'django_bootstrap5',

]

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://127.0.0.1',
    'https://localhost',
    'https://0.0.0.0',
    'https://*.broteamracing.ru',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'btr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'btr' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'btr.context_processors.common_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'btr.wsgi.application'

AUTH_USER_MODEL = 'users.SiteUser'

AUTHENTICATION_BACKENDS = [
    'btr.auth.auth_backends.MultiplyFieldBackend',
]

CONN_MAX_AGE = 500

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

if os.getenv('LANGUAGE'):
    LANGUAGE_CODE = os.getenv('LANGUAGE')
else:
    LANGUAGE_CODE = 'ru-ru'

LOCALE_PATHS = [
    BASE_DIR / "btr" / "locale"
]

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)

if DB == 'lite':

    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

elif DB == 'postgres':

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'prod_static')]

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# smtp

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# redis related setup

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'check-booking-status': {
        'task': 'btr.tasks.bookings.check_booking_status',
        'schedule': 25.0,
    },
}

# tg bot setup

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_ADMIN_PASSWORD = os.getenv('TG_ADMIN_PASSWORD')

# YANDEX setup

YANDEX_VERIFICATION_ID = os.getenv('YANDEX_VERIFICATION_ID')
