# mysite/settingsDev.py
import os
from dotenv import load_dotenv
from .settingsBase import *

load_dotenv()  # lee tu .env local si querés

DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
BASE_DIR = Path(__file__).resolve().parent.parent
# BD local (SQLite por defecto)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Archivos estáticos en dev: Django los sirve sin Whitenoise
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
