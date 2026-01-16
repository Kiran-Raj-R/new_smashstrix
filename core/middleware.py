from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path.startswith("/user") or request.path in ["/","/home/","/shop/"]:
                if request.user.is_staff:
                    logout(request)
                    request.session.flush()
                    messages.error(request, "Admin accounts cannot access user pages.")
                    return redirect("login")
        
            if request.path.startswith("/adminpanel"):
                if not request.user.is_staff:
                    logout(request)
                    request.session.flush()
                    messages.error(request,"Unauthorised access.")
                    return redirect("login")
        return self.get_response(request)