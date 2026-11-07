"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from  .import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', views.homepage, name='homepage'),
    path('home/', views.homepage, name='home'),
    path('index/', views.homepage, name='index'),
    path('produk/<slug:kategori_slug>/<slug:slug>/', views.buku_detail, name='buku_detail'),
    path('produk/<slug:slug>/', views.buku_detail, name='buku_detail_simple'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('artikel/', views.article_list, name='article_list'),
    path('artikel/<slug:slug>/', views.article_detail, name='article_detail'),
    path('aktivitas/', views.aktivitas_list, name='aktivitas_list'),
    path('aktivitas/<slug:slug>/', views.aktivitas_detail, name='aktivitas_detail'),
    path('kontak/', views.contact_page, name='contact_page'),
    path('struktur-organisasi/', views.struktur_organisasi, name='struktur_organisasi'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path('dashboard/sebaran/', views.public_dashboard_sebaran, name='public_dashboard_sebaran'),
    path('dashboard/anggota/', views.public_dashboard_anggota, name='public_dashboard_anggota'),
    path('dashboard/institusi/', views.public_dashboard_institusi, name='public_dashboard_institusi'),
    path('call/jurnal/list/', views.journal_list, name='journal_list'),
    path('katalog-pelatihan/', views.katalog_pelatihan, name='katalog_pelatihan'),
    path('app/', include(('app.urls', 'app'), namespace='app')),
    path('login/', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('logout/', views.LogoutView, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)