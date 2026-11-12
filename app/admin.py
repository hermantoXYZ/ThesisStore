from app.models import NoSuratThesis
from django.contrib import admin
from .models import (
    UserPengguna,
    UserAdmin,
    Provinsi,
    BidangPenelitian,
    CategoryBooks,
    Books,
    MediaBooks,
    KerjaSama,
    WebSetting,
    HeroSlide,
    DokumentasiArticle,
    DokumentasiPage,
    Course,
    CourseAgenda,
    Article,
    Page,
    Category,
    JurnalMaster,
    KodeSurat,
    Cart,
    CartItem,
    Order,
    OrderItem,
)

admin.site.register(CategoryBooks)
admin.site.register(Books)
admin.site.register(MediaBooks)
admin.site.register(UserPengguna)
admin.site.register(UserAdmin)
admin.site.register(Provinsi)
admin.site.register(BidangPenelitian)
admin.site.register(KerjaSama)
admin.site.register(WebSetting)
admin.site.register(HeroSlide)
admin.site.register(DokumentasiArticle)
admin.site.register(DokumentasiPage)
admin.site.register(Course)
admin.site.register(CourseAgenda)
admin.site.register(Article)
admin.site.register(Page)
admin.site.register(Category)
admin.site.register(JurnalMaster)
admin.site.register(KodeSurat)
admin.site.register(NoSuratThesis)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

