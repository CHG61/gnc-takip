import os
from pathlib import Path

# --- Yol/Temel ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- .env yardımcıları ---
def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(int(default)))
    return v.lower() in ("1", "true", "yes", "on")

# --- Çekirdek ayarlar ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-keep-secret-local")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# --- Uygulamalar ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pages.apps.PagesConfig",
]

# --- Middleware (Whitenoise dahil) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # statik dosyalar için
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gncsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gncsite.wsgi.application"

# --- Veritabanı: SADECE SQLite ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Parola doğrulama ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Yerelleştirme ---
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True  # (Django 4.1'de USE_L10N artık gereksiz)

# --- Statik / Medya ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]           # geliştirme sırasında
STATIC_ROOT = BASE_DIR / "staticfiles"             # collectstatic hedefi

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django 4.1.x için Whitenoise storage ayarı:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Varsayılan PK tipi ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
