from datetime import datetime


class RequestLoggingMiddleware:
    """
    Middleware that logs each user's request to the requests.log file.

    Log format:
        f"{datetime.now()} - User: {user} - Path: {request.path}"
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = "requests.log"

    def __call__(self, request):
        # get username or AnonymousUser
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            user = "AnonymousUser"

        # EXACT format requested in the task
        line = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        # append to requests.log
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

        response = self.get_response(request)
        return response

from datetime import datetime, timedelta
from collections import defaultdict, deque

from django.http import HttpResponseForbidden, HttpResponse
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware:
    """
    Basic middleware that logs each user's requests to requests.log file.

    Log format:
    "{datetime.now()} - User: {user} - Path: {request.path}"
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = 'requests.log'

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            user_repr = 'AnonymousUser'
        else:
            user_repr = str(user)

        line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception:
            # Fail silently in case of file system issues
            pass

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the chat during certain hours.

    If a user accesses the chat outside 9AM and 6PM (server time),
    it returns 403 Forbidden.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only restrict access to chat-related URLs
        path = request.path or ''
        if '/messages' in path or '/conversations' in path:
            now = datetime.now().time()
            # Allowed hours: between 9:00 and 18:00 (9AM - 6PM)
            if not (9 <= now.hour < 18):
                return HttpResponseForbidden('Chat access is restricted at this time.')

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages (POST requests)
    a user can send within a certain time window, based on their IP address.

    - Tracks the number of POST requests per IP.
    - Allows up to 5 messages per 1-minute window.
    - If the limit is exceeded, blocks further messaging.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Map ip -> deque of timestamps
        self.ip_requests = defaultdict(deque)
        self.time_window = timedelta(minutes=1)
        self.max_requests = 5

    def __call__(self, request):
        # We only care about POST requests that represent new messages
        if request.method == 'POST' and ('/messages' in request.path):
            ip_address = self._get_ip(request)
            now = datetime.now()

            timestamps = self.ip_requests[ip_address]

            # Remove timestamps outside the time window
            while timestamps and (now - timestamps[0]) > self.time_window:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                # Too many requests in the last minute
                return HttpResponse(
                    'Rate limit exceeded: too many messages from this IP.',
                    status=429
                )

            timestamps.append(now)

        return self.get_response(request)

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class RolepermissionMiddleware:
    """
    Middleware that checks the user's role before allowing access
    to specific actions.

    - If the user is not admin or moderator, return 403 for restricted actions.
    - Here, we treat "admin or moderator" as:
        * is_superuser or is_staff
        * OR belonging to a group named 'admin' or 'moderator'.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only restrict for modifying actions on chat endpoints
        restricted_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        path = request.path or ''

        if any(segment in path for segment in ['/messages', '/conversations']):
            if request.method in restricted_methods:
                user = getattr(request, 'user', None)

                if user is None or not user.is_authenticated:
                    return HttpResponseForbidden('You must be logged in.')

                # Determine if user is admin or moderator
                is_admin_like = user.is_staff or user.is_superuser
                has_role_group = user.groups.filter(name__in=['admin', 'moderator']).exists()

                if not (is_admin_like or has_role_group):
                    return HttpResponseForbidden('You do not have permission to perform this action.')

        return self.get_response(request)
