from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Login required.")
            if request.user.role != required_role:
                raise PermissionDenied("You do not have access to this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
