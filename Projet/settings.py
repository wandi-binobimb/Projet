import os
from pathlib import Path
from decouple import config
import dj_database_url
import cloudinary

# ======================
# المسار الأساسي للمشروع
# ======================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# إعدادات الأمان
# ======================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')

# ⚠️ أثناء النشر اجعلها False — لتجنب عرض الأخطاء
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']

# ======================
# التطبيقات المثبتة
# ======================
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # مكتبات Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # تطبيقك
    'store',

    # أدوات إضافية
    'django_extensions',
]

# ======================
# Middleware
# ======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ ضروري لـ Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Projet.urls'

# ======================
# القوالب
# ======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.panier_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Projet.wsgi.application'

# ======================
# قاعدة البيانات (Render/PostgreSQL أو SQLite)
# ======================
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# ======================
# اللغة والمنطقة الزمنية
# ======================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================
# إعدادات STATIC (WhiteNoise)
# ======================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ======================
# إعدادات MEDIA عبر Cloudinary
# ======================
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

# ======================
# إعداد Cloudinary
# ======================
cloudinary.config(
    cloud_name="dcssekkd5",
    api_key="671348262812769",
    api_secret="WEgRFtuTs9WpIJkLgEtckj3HUSE",
)

# ======================
# الكاش المحلي لتسريع الصفحات
# ======================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ======================
# تحسين إضافي للأداء
# ======================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

WHITENOISE_USE_FINDERS = True
