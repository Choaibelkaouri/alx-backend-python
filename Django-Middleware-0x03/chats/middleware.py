from datetime import datetime, timedelta
from collections import defaultdict, deque

from django.http import HttpResponseForbidden, HttpResponse


class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to requests.log.

    In __call__ it logs:
        f"{datetime.now()} - User: {user} - Path: {request.path}"
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = "requests.log"

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            user_repr = "AnonymousUser"
        else:
            user_repr = str(user)

        line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the chat during certain hours.

    If a user accesses the chat outside 9PM and 6PM (server time),
    it returns 403 Forbidden.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ""
        if "/messages" in path or "/conversations" in path:
            now = datetime.now().time()
            # Simple interpretation of "outside 9PM and 6PM":
            # allow only between 18:00 and 21:00
            if not (18 <= now.hour < 21):
                return HttpResponseForbidden("Chat access is restricted at this time.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.

    - Tracks POST requests to /messages.
    - Allows up to 5 messages per 1-minute window per IP.
    - If the limit is exceeded, it blocks further messages.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_requests = defaultdict(deque)
        self.time_window = timedelta(minutes=1)
        self.max_requests = 5

    def __call__(self, request):
        if request.method == "POST" and "/messages" in (request.path or ""):
            ip_address = self._get_ip(request)
            now = datetime.now()

            timestamps = self.ip_requests[ip_address]

            while timestamps and (now - timestamps[0]) > self.time_window:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                return HttpResponse(
                    "Rate limit exceeded: too many messages from this IP.",
                    status=429,
                )

            timestamps.append(now)

        return self.get_response(request)

    def _get_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RolepermissionMiddleware:
    """
    Middleware that checks the user's role before allowing access
    to specific actions.

    - If the user is not admin or moderator, it returns 403 for restricted actions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_methods = ["POST", "PUT", "PATCH", "DELETE"]
        path = request.path or ""

        if any(seg in path for seg in ["/messages", "/conversations"]):
            if request.method in restricted_methods:
                user = getattr(request, "user", None)

                if user is None or not getattr(user, "is_authenticated", False):
                    return HttpResponseForbidden("You must be logged in.")

                is_admin_like = user.is_superuser or user.is_staff
                has_role_group = user.groups.filter(
                    name__in=["admin", "moderator"]
                ).exists()

                if not (is_admin_like or has_role_group):
                    return HttpResponseForbidden(
                        "You do not have permission to perform this action."
                    )

        return self.get_response(request)
