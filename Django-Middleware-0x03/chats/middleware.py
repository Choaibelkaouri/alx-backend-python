from datetime import datetime


class RequestLoggingMiddleware:
    """
    Middleware that logs each user's request to the requests.log file.

    It must log EXACTLY this information in __call__:

        f"{datetime.now()} - User: {user} - Path: {request.path}"
    """

    def __init__(self, get_response):
        # get_response is the next middleware or the view
        self.get_response = get_response
        # log file at the project root (Django-Middleware-0x03/requests.log)
        self.log_file = "requests.log"

    def __call__(self, request):
        # Get the user or fall back to AnonymousUser
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            user = "AnonymousUser"

        # EXACT format requested in the instructions
        line = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        # Append to requests.log
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

        # Continue the request/response cycle
        response = self.get_response(request)
        return response
