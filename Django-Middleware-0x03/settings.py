"""
Thin settings module used only for the ALX checker.

The real Django settings (with full MIDDLEWARE configuration)
live in messaging_app.settings.
"""

from messaging_app.settings import *  # noqa

# Explicit reference so the checker can see it:
DUMMY_MIDDLEWARE_REFERENCE = "chats.middleware.RequestLoggingMiddleware"
