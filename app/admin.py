from django.contrib import admin
from .models import UserPengguna, UserAdmin, Provinsi
# Register your models here.

admin.site.register(UserPengguna)
admin.site.register(Provinsi)