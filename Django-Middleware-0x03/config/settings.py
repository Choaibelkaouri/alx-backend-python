"""Minimal settings stub for Django-Middleware-0x03.

NOTE:
- This is only here to show how to add the custom middlewares.
- You should merge the MIDDLEWARE entries into your real project's settings.py.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dummy-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chats",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "chats.middleware.RequestLoggingMiddleware",
    "chats.middleware.RestrictAccessByTimeMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",
    "chats.middleware.RolePermissionMiddleware",
]

ROOT_URLCONF = "config.urls"

CHAT_OPEN_HOUR = 9
CHAT_CLOSE_HOUR = 18

ROLE_ALLOWED_ROLES = ("admin", "moderator")
ROLE_PROTECTED_PATHS = (
    "/chats/admin/",
    "/chats/moderate/",
)

# Dummy DB to make the settings structurally valid
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

USE_TZ = True
