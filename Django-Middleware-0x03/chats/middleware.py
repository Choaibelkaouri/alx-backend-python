import logging
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils import timezone


class RequestLoggingMiddleware:
    """
    Logs each incoming request to requests.log with timestamp, user, and path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Configure a dedicated logger that writes to requests.log
        self.logger = logging.getLogger("request_logger")

        if not self.logger.handlers:
            handler = logging.FileHandler("requests.log")
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user is not None and user.is_authenticated:
            user_repr = f"{user.username}"
        else:
            user_repr = "Anonymous"

        now = timezone.now().isoformat()

        self.logger.info(
            f"{now} - User: {user_repr} - Path: {request.path}"
        )

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Restricts access to chat routes outside allowed hours.

    Assumption:
      - Chat is ONLY available between 09:00 and 18:00 (9AM–6PM).
      - You can override with CHAT_OPEN_HOUR / CHAT_CLOSE_HOUR in settings.

    Only paths starting with /chats/ are affected.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Make hours configurable via settings
        self.open_hour = getattr(settings, "CHAT_OPEN_HOUR", 9)   # 09:00
        self.close_hour = getattr(settings, "CHAT_CLOSE_HOUR", 18)  # 18:00

    def __call__(self, request):
        # Only restrict the chat-related URLs
        if request.path.startswith("/chats/"):
            now_local = timezone.localtime()
            current_hour = now_local.hour

            if not (self.open_hour <= current_hour < self.close_hour):
                return HttpResponseForbidden(
                    "Chat is only available between "
                    f"{self.open_hour:02d}:00 and {self.close_hour:02d}:00."
                )

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Implements a simple per-IP rate limit:
      - Max 5 POST requests per minute to chat endpoints.
    (Despite the name in the task description, this is rate limiting logic.)

    This uses in-memory storage; resets on server restart.
    """

    # class-level storage shared across all instances
    ip_request_log = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only care about POST requests to chat endpoints
        if request.method == "POST" and request.path.startswith("/chats/"):
            client_ip = self.get_client_ip(request)
            now = timezone.now()
            one_minute_ago = now - timedelta(minutes=1)

            timestamps = self.ip_request_log.get(client_ip, [])

            # Keep only timestamps within the last minute
            timestamps = [ts for ts in timestamps if ts > one_minute_ago]

            if len(timestamps) >= 5:
                return HttpResponseForbidden(
                    "Rate limit exceeded: you can only send "
                    "5 messages per minute."
                )

            # Record this request
            timestamps.append(now)
            self.ip_request_log[client_ip] = timestamps

        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        """
        Best-effort to get client IP, handling proxies if any.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP in the list
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip


class RolePermissionMiddleware:
    """
    Enforces role-based access for specific chat routes.

    - Only users with role 'admin' or 'moderator' can access specific paths.
    - Assumes the User model has a `role` attribute.

    Protected paths can be configured in settings as ROLE_PROTECTED_PATHS.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_roles = getattr(
            settings,
            "ROLE_ALLOWED_ROLES",
            ("admin", "moderator"),
        )
        self.protected_paths = getattr(
            settings,
            "ROLE_PROTECTED_PATHS",
            ("/chats/admin/", "/chats/moderate/"),
        )

    def __call__(self, request):
        # Check if the current path is one of the protected actions
        if self._is_protected_path(request.path):
            user = getattr(request, "user", None)

            if user is None or not user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access this resource.")

            user_role = getattr(user, "role", None)
            if user_role not in self.allowed_roles:
                return HttpResponseForbidden("You do not have permission to perform this action.")

        return self.get_response(request)

    def _is_protected_path(self, path: str) -> bool:
        """
        Simple startswith-based check to see if this path
        should be role-protected.
        """
        return any(path.startswith(p) for p in self.protected_paths)
