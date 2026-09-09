import os
import secrets
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# Never commit a production secret. Set SECRET_KEY in Vercel; the generated
# fallback keeps local/demo instances bootable without exposing credentials.
SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(50)

DEBUG = os.getenv('DEBUG', 'False' if os.getenv('VERCEL') else 'True').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in (
        os.getenv('ALLOWED_HOSTS')
        or '.vercel.app,greenhealth-indol.vercel.app,127.0.0.1,localhost'
    ).split(',')
    if host.strip()
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'crops.apps.CropsConfig',
    'diseases.apps.DiseasesConfig',
    'knowledge_base.apps.KnowledgeBaseConfig',
    'ml_model.apps.MlModelConfig',
    'diagnosis.apps.DiagnosisConfig',
    'reports.apps.ReportsConfig',
]

# Django 5.2 reads STORAGES, not the removed DEFAULT_FILE_STORAGE setting.
CLOUDINARY_CONFIGURED = bool(os.getenv('CLOUDINARY_URL') or all(os.getenv(key) for key in (
    'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET')))
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
if CLOUDINARY_CONFIGURED:
    INSTALLED_APPS.insert(0, 'cloudinary_storage')
    INSTALLED_APPS.append('cloudinary')
    CLOUDINARY_STORAGE = {'SECURE': True}
    if not os.getenv('CLOUDINARY_URL'):
        CLOUDINARY_STORAGE.update({
            'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
            'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
        })
    STORAGES['default'] = {'BACKEND': 'core.storage.BoundedCloudinaryStorage'}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.platform_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Configuration
import dj_database_url

if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.getenv('DB_ENGINE') == 'postgresql' or os.getenv('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'agri_plant_health'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('POSTGRES_HOST', 'db'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
else:
    # Writable location for Vercel Serverless environment
    db_path = BASE_DIR / 'db.sqlite3'
    if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_dir = Path('/tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        db_path = tmp_dir / 'db.sqlite3'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(db_path),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
]

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_MANIFEST_STRICT = False
# Serverless builds do not need a checked-in collectstatic directory.
WHITENOISE_USE_FINDERS = bool(os.getenv('VERCEL'))

# Media files (Uploaded images & generated PDF reports)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
    MEDIA_ROOT = Path('/tmp/media')
    os.makedirs(MEDIA_ROOT, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'diagnosis': '12/minute', 'feedback': '30/minute'},
}

# CORS and CSRF settings
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [
    'https://greenhealth-indol.vercel.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]
CSRF_TRUSTED_ORIGINS += [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
for host_key in ('VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL'):
    if os.getenv(host_key):
        CSRF_TRUSTED_ORIGINS.append('https://' + os.environ[host_key])

# Security Settings
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
MESSAGE_TAGS = {40: 'danger'}

# Platform Custom Settings
DEMO_MODE = os.getenv('DEMO_MODE', 'True').lower() == 'true'
AI_PROVIDER = (os.getenv('AI_PROVIDER') or 'gemini').strip().lower()
ENABLE_AI_GENERATION = os.getenv('ENABLE_AI_GENERATION', 'true').strip().lower() in ('true', '1', 'yes', 'on')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = (os.getenv('GEMINI_MODEL') or 'gemini-3.1-flash-lite').strip().removeprefix('models/')
try:
    GEMINI_TIMEOUT_SECONDS = max(5, min(120, int(os.getenv('GEMINI_TIMEOUT_SECONDS') or '60')))
except ValueError:
    GEMINI_TIMEOUT_SECONDS = 60
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD') or '0.60')
CONSISTENCY_THRESHOLD = float(os.getenv('CONSISTENCY_THRESHOLD') or '0.50')
MAX_DIAGNOSIS_IMAGES = 5
MIN_DIAGNOSIS_IMAGES = 1
MAX_UPLOAD_BYTES = 4 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_BYTES
DATA_UPLOAD_MAX_NUMBER_FILES = 10
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_BYTES

# Image retention policy default ('TEMPORARY', 'PROCESSED', 'STORED_WITH_USER_PERMISSION', 'DELETED')
DEFAULT_IMAGE_RETENTION_POLICY = os.getenv('IMAGE_RETENTION_POLICY', 'PROCESSED')
