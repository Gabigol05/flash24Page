from .settingsDev import *

# 🔒 Seguridad
DEBUG = False

# ✅ Hosts permitidos
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 🗃️ Base de datos (se puede seguir usando SQLite o cambiar a PostgreSQL más adelante)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'nombre_base',
#         'USER': 'usuario',
#         'PASSWORD': 'contraseña',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# 📁 Archivos estáticos para producción
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🪵 Logging: errores van a archivo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'errores.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
