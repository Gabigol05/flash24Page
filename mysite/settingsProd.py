# mysite/settingsProd.py
import os
import dj_database_url
from .settingsBase import *

DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")  # en Render la seteás en Environment
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no configurada en producción")

ALLOWED_HOSTS = [".onrender.com"]  # sumá tu dominio si usás uno

# Base de datos desde DATABASE_URL (Render te la da)
DATABASES = {
    "default": dj_database_url.config(conn_max_age=60, ssl_require=False)
}

# Whitenoise para servir estáticos
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Seguridad mínima sensata
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
