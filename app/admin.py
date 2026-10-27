from django.contrib import admin
from .models import (
    UserPengguna,
    UserAdmin,
    Provinsi,
    BidangPenelitian,
    CategoryBooks,
    Books,
    MediaBooks
)

admin.site.register(CategoryBooks)
admin.site.register(Books)
admin.site.register(MediaBooks)
admin.site.register(UserPengguna)
admin.site.register(UserAdmin)
admin.site.register(Provinsi)
admin.site.register(BidangPenelitian)