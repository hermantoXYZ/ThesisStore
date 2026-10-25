from django.shortcuts import redirect
from django.contrib import messages
from .models import UserAdmin 
from functools import wraps

def check_useradmin(function):
    def wrapper(request, *args, **kwargs):   
        useradmin = UserAdmin.objects.get(username=request.user)
        request.useradmin = useradmin
        if useradmin.photo == None :
            messages.error(request, "Lengkapi data anda terlebih dahulu!")
            return redirect('app:profile_admin')               
        return function(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.last_name == "Super Admin":
            return view_func(request, *args, **kwargs)
        else:
            return redirect('app:dashboard')
    return _wrapped_view