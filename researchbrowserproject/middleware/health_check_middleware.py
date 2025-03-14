# taken from: https://github.com/Hovercross/django-lb-health-check/blob/main/lb_health_check/middleware.py

import logging
from typing import List

from django.conf import settings
from django.http import HttpResponse

log = logging.getLogger(__name__)

COMMON_MIDDLEWARE = "django.middleware.common.CommonMiddleware"
SECURITY_MIDDLEWARE = "django.middleware.security.SecurityMiddleware"

# Middleware that the AliveCheck must come before
MUST_ABOVE = [COMMON_MIDDLEWARE, SECURITY_MIDDLEWARE]


class AliveCheck:
    """A simple "am I responding to HTTP requests" check
    that is designed to be hit from a load balancer"""

    def __init__(self, get_response):
        self.get_response = get_response

        # I only want to warn and not disable because it's possible to do some trickery
        # in the ALLOWED_HOSTS or common middleware to still respond properly
        _check_middleware_position()

        self.urls = ["/health-check"]

        if not self.urls:
            log.error("No aliveness URLs are defined, check disabled")

        for url in self.urls:
            log.info("Intercepting GET requests to %s for aliveness check", url)

    def __call__(self, request):
        # Intercept health check URL calls so
        # they bypass the allowed hosts check

        if request.method == "GET" and request.path in self.urls:
            return HttpResponse("200 OK\n", content_type="text/plain")

        # Process the request as normal if it isn't a health check
        return self.get_response(request)

    @classmethod
    def get_import_name(cls) -> str:
        return f"{cls.__module__}.{cls.__name__}"


def _get_middleware() -> List[str]:
    try:
        return settings.MIDDLEWARE
    except AttributeError:
        log.debug("middleware not defined in settings")
        return []


def _check_middleware_position():
    """Warn if the middleware is in the wrong position"""

    middleware = _get_middleware()

    try:
        my_position = middleware.index(AliveCheck.get_import_name())
    except ValueError:
        # We can't do anything intelligent if we aren't in the middleware,
        # though it's highly unlikely that this will be called if that is the case
        log.warning("AliveCheck not found in middleware")
        return

    for name in MUST_ABOVE:
        try:
            pos = middleware.index(name)
        except ValueError:
            # If this middleware isn't in the list, it's OK
            log.debug("%s not in middleware", name)
            continue

        if pos < my_position:
            log.warning(
                "%s is before %s in middleware. "
                "Aliveness check may not work properly",
                name,
                AliveCheck.get_import_name(),
            )
