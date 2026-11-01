from django.conf import settings
from django.http import HttpResponse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        maintenance = getattr(settings, "MAINTENANCE_MODE", False)

        if maintenance and not request.path.startswith("/admin/"):
            return HttpResponse("Site is under maintenance", status=503)

        return self.get_response(request)