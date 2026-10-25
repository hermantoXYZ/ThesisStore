from django.shortcuts import redirect
from django.contrib import messages
from .models import UserPengguna 
from functools import wraps

def check_userpengguna(function):
    def wrapper(request, *args, **kwargs):
        userpengguna = UserPengguna.objects.filter(user=request.user).first()
        request.userpengguna = userpengguna
        if not userpengguna or userpengguna.photo == None or userpengguna.gender == None:
            messages.error(request, "Lengkapi data anda terlebih dahulu!")
            return redirect('app:profile_pengguna')               
        return function(request, *args, **kwargs)
    return wrapper

def pengguna_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.last_name != "Pengguna":
            return redirect('app:dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
