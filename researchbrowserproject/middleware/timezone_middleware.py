import zoneinfo

from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            tzname = request.session.get('django_timezone')
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                if request.user.is_authenticated:
                    request.session['django_timezone'] = request.user.profile.timezone
                    timezone.activate(zoneinfo.ZoneInfo(request.session['django_timezone']))
                else:
                    timezone.activate(zoneinfo.ZoneInfo("UTC"))
            return self.get_response(request)
        except:
            return self.get_response(request)