import os
from pathlib import Path
from decouple import config
import cloudinary

# ----------------------
# المسار الأساسي للمشروع
# ----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# إعدادات الأمان
# ----------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')
DEBUG = True  # اجعله True فقط عند التجربة محلياً
ALLOWED_HOSTS = ['*']

# ----------------------
# التطبيقات المثبتة
# ----------------------
INSTALLED_APPS = [
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

# ----------------------
# Middleware
# ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # لتقديم ملفات static على Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Projet.urls'

# ----------------------
# القوالب
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
# اللغة والمنطقة الزمنية
# ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------
# ملفات STATIC
# ----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------
# إعدادات MEDIA عبر Cloudinary
# ----------------------
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

# ----------------------
# إعداد Cloudinary
# ----------------------
cloudinary.config(
    cloudinary_url=config('CLOUDINARY_URL')
)


import os
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api

# === إعداد Cloudinary ===
cloudinary.config(
    cloud_name="dcssekkd5",
    api_key="671348262812769",
    api_secret="WEgRFtuTs9WpIJkLgEtckj3HUSE"
)

# === إعداد ملفات الميديا ===
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
