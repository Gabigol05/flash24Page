# mysite/settings/base.py
from pathlib import Path
import os
from django.db.backends.signals import connection_created
from django.dispatch import receiver

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad básica ---
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-*yx!7p*lt5!6*ae8wa0g@u+6l#_k1j27v)2r-&mq_c)tsgdn32'  # fallback local
)
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# --- Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'first',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # agrega tu carpeta templates si la tenés
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# =========================================================
# BASE DE DATOS (conmutador por variables de entorno)
# ---------------------------------------------------------
# Por defecto usa SQLite (ideal para PythonAnywhere con 1 instancia).
# Si definís DB_ENGINE=postgres o mysql en variables de entorno,
# cambia automáticamente a ese motor.
# =========================================================

DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').lower()

if DB_ENGINE in ('sqlite', 'sqlite3'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.getenv('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
            # timeout ayuda a evitar "database is locked" con leves concurrencias
            'OPTIONS': {'timeout': int(os.getenv('DB_TIMEOUT', '20'))},
            # Envuelve cada request en transacción (consistencia simple)
            'ATOMIC_REQUESTS': True,
        }
    }

    # Tuning: WAL + synchronous=NORMAL para permitir lecturas mientras se escribe
    @receiver(connection_created)
    def _sqlite_pragmas(sender, connection, **kwargs):
        if connection.vendor == "sqlite":
            cur = connection.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("PRAGMA synchronous=NORMAL;")

elif DB_ENGINE in ('postgres', 'postgresql'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),  # conexiones persistentes
            'ATOMIC_REQUESTS': True,
        }
    }
elif DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
            'ATOMIC_REQUESTS': True,
        }
    }
else:
    raise RuntimeError(f"DB_ENGINE desconocido: {DB_ENGINE}")

# --- i18n / zona horaria ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Está ticos / media ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # destino de collectstatic
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
