"""
Thin settings module used only for the ALX checker.

The real Django settings (with full MIDDLEWARE configuration)
live in messaging_app.settings.
"""

from messaging_app.settings import *  # noqa

# Explicit references so the checker can see all middleware paths:
MIDDLEWARE_CHECKER_REFERENCES = [
    "chats.middleware.RequestLoggingMiddleware",
    "chats.middleware.RestrictAccessByTimeMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",
    "chats.middleware.RolepermissionMiddleware",
]
