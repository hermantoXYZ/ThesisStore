from django.urls import path
from . import views
from . import views_admin
from . import views_pengguna


urlpatterns = [
    ###### ADMIN KEANGGOTAAN INDIVIDU ######   
    path('profile/admin', views_admin.profile_admin, name='profile_admin'),

    ###### KATEGORI BUKU ######
    path('buku/kategori/', views_admin.kategori_buku_list, name='kategori_buku_list'),
    path('buku/kategori/tambah/', views_admin.kategori_buku_tambah, name='kategori_buku_tambah'),
    path('buku/kategori/edit/<uuid:uuid>/', views_admin.kategori_buku_edit, name='kategori_buku_edit'),
    path('buku/kategori/hapus/<uuid:uuid>/', views_admin.kategori_buku_hapus, name='kategori_buku_hapus'),

    ###### KELOLA BUKU ###### 
    path('buku/', views_admin.buku_list, name='buku_list'),
    path('buku/tambah/', views_admin.buku_tambah, name='buku_tambah'),
    path('buku/edit/<uuid:uuid>/', views_admin.buku_edit, name='buku_edit'),
    path('buku/hapus/<uuid:uuid>/', views_admin.buku_hapus, name='buku_hapus'),
    path('buku/<uuid:book_uuid>/media/hapus/<uuid:media_uuid>/', views_admin.buku_media_hapus, name='buku_media_hapus'),

    ###### KELOLA ARTIKEL / BERITA ######
    path('admin/article', views_admin.article_list, name='admin_article_list'),
    path('admin/article/create', views_admin.article_create, name='admin_article_create'),
    path('admin/article/<uuid:article_id>/edit', views_admin.article_edit, name='admin_article_edit'),
    path('admin/article/<uuid:article_id>/delete', views_admin.article_delete, name='admin_article_delete'),
    path('admin/article/dokumentasi/<uuid:foto_id>/delete', views_admin.delete_dokumentasi_article, name='admin_delete_dokumentasi_article'),

    ###### KELOLA KATEGORI BERITA ######
    path('admin/category', views_admin.category_list, name='admin_category_list'),
    path('admin/category/<uuid:category_id>/delete', views_admin.category_delete, name='admin_category_delete'),

      ###### KELOLA HALAMAN (PAGE) ######
    path('admin/page', views_admin.page_list, name='admin_page_list'),
    path('admin/page/create', views_admin.page_create, name='admin_page_create'),
    path('admin/page/<uuid:page_id>/edit', views_admin.page_edit, name='admin_page_edit'),
    path('admin/page/<uuid:page_id>/delete', views_admin.page_delete, name='admin_page_delete'),
    path('admin/page/dokumentasi/<uuid:foto_id>/delete', views_admin.delete_dokumentasi_page, name='admin_delete_dokumentasi_page'),

    ###### KELOLA KERJA SAMA / MITRA ######
    path('admin/kerjasama', views_admin.kerjasama_list, name='admin_kerjasama_list'),
    path('admin/kerjasama/<uuid:kerjasama_id>/edit', views_admin.kerjasama_edit, name='admin_kerjasama_edit'),
    path('admin/kerjasama/<uuid:kerjasama_id>/delete', views_admin.kerjasama_delete, name='admin_kerjasama_delete'),

    ###### KELOLA HERO SLIDES (BERANDA) ######
    path('admin/hero-slides', views_admin.hero_slide_list, name='admin_hero_slide_list'),
    path('admin/hero-slides/create', views_admin.hero_slide_create, name='admin_hero_slide_create'),
    path('admin/hero-slides/<uuid:slide_id>/edit', views_admin.hero_slide_edit, name='admin_hero_slide_edit'),
    path('admin/hero-slides/<uuid:slide_id>/delete', views_admin.hero_slide_delete, name='admin_hero_slide_delete'),

    ###### PENGATURAN WEBSITE ######
    path('admin/web-setting', views_admin.web_setting_view, name='admin_web_setting'),
    
    ###### PENGUNA/CLIENTS #######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),

    ###### UMUM ######         
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),      
]