from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.cache import add_never_cache_headers

class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        path = request.path
        
        if user.is_authenticated:
            if hasattr(user, "blocked") and user.blocked:
                logout(request)
                request.session.flush()
                messages.error(request, "Your account has been blocked.")
                return redirect("login")

            if path.startswith("/adminpanel") and not user.is_staff:
                messages.error(request, "Unauthorized admin access.")
                return redirect("login")
        
        response = self.get_response(request)
        if user.is_authenticated:
            add_never_cache_headers(response)

        return response
