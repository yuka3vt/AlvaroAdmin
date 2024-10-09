from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth import logout

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/') 
            if request.user.role.capitalize() not in [role.capitalize() for role in allowed_roles]:
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator