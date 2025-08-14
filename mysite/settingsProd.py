# mysite/settings/prod.py
from .base import *
import os

# Producción: sin debug
DEBUG = False

# Dominios permitidos (ajusta con tu usuario/dominio real)
ALLOWED_HOSTS = [
    'tuusuario.pythonanywhere.com',
    'tudominio.com',
    'www.tudominio.com',
]

# CSRF: orígenes de confianza (HTTPS)
CSRF_TRUSTED_ORIGINS = [
    'https://tuusuario.pythonanywhere.com',
    'https://tudominio.com',
    'https://www.tudominio.com',
]

# PythonAnywhere está detrás de proxy: esto hace que Django reconozca HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies seguras si usás HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# (Opcional, habilitalo cuando verifiques HTTPS ok)
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Whitenoise para servir estáticos comprimidos desde la app
# (recordá: pip install whitenoise)
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# En producción EXIGIMOS que la SECRET_KEY venga del entorno
SECRET_KEY = os.environ['SECRET_KEY']
