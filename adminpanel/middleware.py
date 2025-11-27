from django.shortcuts import redirect

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):        
        path = request.path
        if path.startswith("/adminpanel/") and not (path.startswith("/adminpanel/login/") or 
                                                    path.startswith("/adminpanel/logout/")):        
            if not request.user.is_authenticated or not request.user.is_staff:
                return redirect("admin_login")
        return self.get_response(request)