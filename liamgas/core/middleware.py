from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last seen and online status
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.last_seen = timezone.now()
            profile.is_online = True
            profile.save()

        response = self.get_response(request)
        return response