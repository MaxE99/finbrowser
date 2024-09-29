import zoneinfo

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:
    """
    Middleware to manage user timezones based on their session or profile settings.

    This middleware checks if the user has a timezone set in their session.
    If it exists, it activates that timezone. If not, and the user is authenticated,
    it retrieves the timezone from the user's profile and sets it in the session.
    If the user is not authenticated or no timezone is found, it defaults to UTC.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware with a callable to get the response.

        Args:
            get_response (callable): A callable that takes a request and returns a response.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Processes the request to activate the appropriate timezone.

        This method checks the session for a timezone. If not found, it checks
        if the user is authenticated to set the timezone from the user's profile.
        If neither is available, it defaults to UTC.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object returned by the get_response callable.
        """
        try:
            tzname = request.session.get("django_timezone")

            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))

            else:
                if request.user.is_authenticated:
                    request.session["django_timezone"] = request.user.profile.timezone
                    timezone.activate(
                        zoneinfo.ZoneInfo(request.session["django_timezone"])
                    )
                else:
                    timezone.activate(zoneinfo.ZoneInfo("UTC"))

            return self.get_response(request)

        except:
            return self.get_response(request)
