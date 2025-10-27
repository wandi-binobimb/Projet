import os
from pathlib import Path
from decouple import config
import cloudinary

# ----------------------
# مسار المشروع
# ----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# إعدادات الأمان
# ----------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['projet-z3f2.onrender.com', 'localhost', '127.0.0.1']

# ----------------------
# تطبيقات المشروع
# ----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # تطبيقك
    'store',

    # أدوات إضافية
    'django_extensions',
]

# ----------------------
# Middleware
# ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # لتقديم static files على Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Projet.urls'

# ----------------------
# Templates
# ----------------------
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

# ----------------------
# قاعدة البيانات
# ----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ----------------------
# الإعدادات العامة
# ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------
# ملفات static
# ----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------
# ملفات media
# ----------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------
# إعداد Cloudinary باستخدام .env
# ----------------------
cloudinary.config(
    cloud_name = config('CLOUDINARY_CLOUD_NAME'),
    api_key = config('CLOUDINARY_API_KEY'),
    api_secret = config('CLOUDINARY_API_SECRET')
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ----------------------
# نصائح للنشر على Render
# ----------------------
# 1. تأكد من أن لديك ملف requirements.txt يحتوي على:
#    django, python-decouple, cloudinary, django-cloudinary-storage, whitenoise
# 2. قبل رفع الموقع نفذ:
#    python manage.py collectstatic --noinput
#    ليتم تجهيز ملفات static للـ Render



