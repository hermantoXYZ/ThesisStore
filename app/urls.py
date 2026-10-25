from django.urls import path

from . import views
from . import views_admin
from . import views_pengguna


urlpatterns = [
    ###### ADMIN KEANGGOTAAN INDIVIDU ######   
    path('profile/admin', views_admin.profile_admin, name='profile_admin'),

    ###### PENGUNA/CLIENTS #######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),

    ###### UMUM ######         
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),      
]