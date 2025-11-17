"""
Thin settings module used only for the ALX checker.

It simply imports everything from the real Django settings module
located in messaging_app.settings, where the MIDDLEWARE configuration
lives (including RequestLoggingMiddleware).
"""

from messaging_app.settings import *  # noqa
