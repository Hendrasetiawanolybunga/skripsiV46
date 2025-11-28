
from pathlib import Path
import os
from django.contrib.messages import constants as messages
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-j+fa$j-w-x7ua4upzterye(*1g7j5clih!9ym)0oo$12wf_bf%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'bluecode2004.pythonanywhere.com']


# Application definition

INSTALLED_APPS = [
    
    'jazzmin',

    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'import_export',
    'django_tables2',
    'django_filters',
    'admin_dashboard',
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

ROOT_URLCONF = 'ProyekBarokah.urls'

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
                'admin_dashboard.context_processors.transaksi_notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'ProyekBarokah.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'id-ID'

TIME_ZONE = 'Asia/Makassar' 

USE_I18N = True

USE_TZ = True

# STATIC_URL adalah URL yang digunakan untuk mereferensikan file statis.
STATIC_URL = '/static/'

# STATICFILES_DIRS adalah direktori tambahan tempat Django harus mencari file statis.
# Tambahkan path ke folder 'static' yang baru Anda buat.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# STATIC_ROOT adalah direktori tempat file statis dikumpulkan untuk produksi.
# Jangan tambahkan file statis di sini secara manual.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# URL yang digunakan saat mereferensikan file media.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

# PENTING: Pastikan variabel DEBUG terdefinisi dengan benar

if DEBUG:
    # Untuk Development/Testing (Tidak mengirim email, hanya mencegah error)
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
else:
    # Untuk Production (Ganti dengan kredensial SMTP PythonAnywhere yang valid)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.hostanda.com' # Placeholder
    EMAIL_PORT = 587 # Placeholder
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'user@domain.com' # Placeholder
    EMAIL_HOST_PASSWORD = 'password-anda' # Placeholder

DEFAULT_FROM_EMAIL = 'admin@barokah.com'

# --- JAZZMIN SETTINGS ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'admin_dashboard.Admin'

JAZZMIN_SETTINGS = {
    "site_title": "Barokah Jaya Beton Admin",
    "site_header": "Barokah Jaya Beton",
    "site_brand": "Barokah Jaya Beton",
    "site_logo": None,
    
    # Menghilangkan Group dan Model Admin (sesuai permintaan user untuk kesederhanaan)
    "hide_models": [
        "auth.Group",
        "admin_dashboard.Admin", # Menyembunyikan model Admin yang Anda buat
        "admin_dashboard.DetailTransaksi", # Biasanya tidak perlu diakses langsung
    ],
    
    # 1. Mengatur Halaman Index Default ke Dashboard Analitik
    "welcome_sign": "Selamat Datang di Dashboard Admin Barokah Jaya Beton",
    "index_title": "Dashboard Admin",
    
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "admin_dashboard.Pelanggan": "fas fa-user-friends",
        "admin_dashboard.Kategori": "fas fa-tags",
        "admin_dashboard.DiskonPelanggan": "fas fa-percent",
        "admin_dashboard.Produk": "fas fa-boxes",
        "admin_dashboard.Transaksi": "fas fa-shopping-cart",
        "admin_dashboard.DetailTransaksi": "fas fa-receipt",
        "admin_dashboard.Notifikasi": "fas fa-bell",
        "admin_dashboard.Karyawan": "fas fa-user-tie",
    },
    
    # 🚨 MODIFIKASI: Mengatur Urutan Menu (order_with_respect_to)
    # KUNCI: Menambahkan "admin_dashboard" di posisi pertama agar custom_links di-prioritaskan
    "order_with_respect_to": [
        "admin_dashboard",             # <-- Menu Kustom Ditarik ke ATAS
        "admin_dashboard.Kategori",    # Kategori
        "admin_dashboard.Produk",      # Produk
        "admin_dashboard.Pelanggan",   # Pelanggan
        "admin_dashboard.Transaksi",   # Transaksi (Induk)
        "admin_dashboard.DiskonPelanggan",# Diskon
        "admin_dashboard.Notifikasi",  # Notifikasi
        "auth", # Menarik model bawaan Django ke bawah (opsional, untuk memastikan auth.User dkk tetap di bawah)
    ],
    
    # 3. Custom Links - Pindahkan Dashboard Analitik ke Paling Atas
    "custom_links": {
        "admin_dashboard": [
            # Sidebar links removed for reports; they'll be available in the top navbar instead
        ],
    },
    # Top navbar links — show report links in the top navigation bar instead of sidebar
    "topmenu_links": [
        {
            "name": "Laporan Transaksi",
            "url": "laporan_transaksi",
            "icon": "fas fa-cash-register"
        },
        {
            "name": "Laporan Produk Terlaris",
            "url": "laporan_produk_terlaris",
            "icon": "fas fa-medal"
        }
    ],
    
    "model_settings": {
        "admin_dashboard.Transaksi": {
            "name": "Transaksi",
            "icon": "fas fa-shopping-cart",
            "badge": "new_transaction_count",
        },
        # Mengubah nama menu bawaan 'Admin' menjadi sesuatu yang lebih umum (opsional)
        "admin_dashboard.Admin": {
            "name": "Pengguna Sistem",
        },
    },

    # 4. Menghilangkan Link User (Admin/User Name) di Navbar Kanan Atas
    # Set ini ke False agar menu setting/logout user tidak muncul
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "search_model": ["admin_dashboard.Produk", "admin_dashboard.Pelanggan"]
}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-navy",
    "navbar": "navbar-lightblue navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-lightblue",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "yeti",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": False
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Makassar'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'check-birthday-and-loyalty-daily': {
        'task': 'admin_dashboard.tasks.check_birthday_and_loyalty_task',
        'schedule': crontab(minute=0, hour=0),  # Run daily at midnight
    },
}

# Channels Configuration
ASGI_APPLICATION = 'ProyekBarokah.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
