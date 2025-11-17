#!/usr/bin/env python
"""Minimal manage.py stub for Django-Middleware-0x03.

This is only for structure; you should use your real project's manage.py.
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it is installed and "
            "available on your PYTHONPATH environment variable."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
