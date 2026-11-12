from django.urls import path
from . import views
from . import views_admin
from . import views_pengguna
from . import views_admin_set
from .view_print import print_loa_jurnal

urlpatterns = [
    ###### ADMIN KEANGGOTAAN INDIVIDU ######   
    path('profile/admin', views_admin_set.profile_admin, name='profile_admin'),
    path('user/list', views_admin_set.user_list, name='user_list'),      
    path('user/edit/<str:id>/<str:role>/', views_admin_set.user_edit, name='user_edit'),

    ###### KATEGORI BUKU ######
    path('buku/kategori/', views_admin.kategori_buku_list, name='kategori_buku_list'),
    path('buku/kategori/tambah/', views_admin.kategori_buku_tambah, name='kategori_buku_tambah'),
    path('buku/kategori/edit/<uuid:uuid>/', views_admin.kategori_buku_edit, name='kategori_buku_edit'),
    path('buku/kategori/hapus/<uuid:uuid>/', views_admin.kategori_buku_hapus, name='kategori_buku_hapus'),

    ###### KELOLA BUKU & PESANAN TOKO ###### 
    path('admin/pesanan/', views_admin.admin_order_list, name='admin_order_list'),
    path('admin/pesanan/<str:order_number>/', views_admin.admin_order_detail, name='admin_order_detail'),
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

    ###### KELOLA COURSE / PELATIHAN ######
    path('admin/course', views_admin.course_list, name='admin_course_list'),
    path('admin/course/create', views_admin.course_create, name='admin_course_create'),
    path('admin/course/<uuid:uuid>/edit', views_admin.course_edit, name='admin_course_edit'),
    path('admin/course/<uuid:uuid>/delete', views_admin.course_delete, name='admin_course_delete'),
    path('admin/course/<uuid:course_uuid>/agenda/add', views_admin.course_agenda_add, name='admin_course_agenda_add'),
    path('admin/course/agenda/<int:agenda_id>/edit', views_admin.course_agenda_edit, name='admin_course_agenda_edit'),
    path('admin/course/agenda/<int:agenda_id>/delete', views_admin.course_agenda_delete, name='admin_course_agenda_delete'),

    ###### MASTER JURNAL ILMIAH ######
    path('admin/jurnal', views_admin.jurnal_list, name='admin_jurnal_list'),
    path('admin/jurnal/tambah', views_admin.jurnal_tambah, name='admin_jurnal_tambah'),
    path('admin/jurnal/<uuid:uuid>/edit', views_admin.jurnal_edit, name='admin_jurnal_edit'),
    path('admin/jurnal/<uuid:uuid>/hapus', views_admin.jurnal_hapus, name='admin_jurnal_hapus'),

    ###### LOA JURNAL (LETTER OF ACCEPTANCE) ######
    path('admin/loa', views_admin.loa_jurnal_list, name='admin_loa_jurnal_list'),
    path('admin/loa/tambah', views_admin.loa_jurnal_tambah, name='admin_loa_jurnal_tambah'),
    path('admin/loa/<uuid:uuid>/edit', views_admin.loa_jurnal_edit, name='admin_loa_jurnal_edit'),
    path('admin/loa/<uuid:uuid>/hapus', views_admin.loa_jurnal_hapus, name='admin_loa_jurnal_hapus'),
    path('admin/loa/<uuid:uuid>/print', print_loa_jurnal.loa_jurnal_print, name='admin_loa_jurnal_print'),
    path('loa/<uuid:uuid>/print', print_loa_jurnal.loa_jurnal_print),

    ###### TATA USAHA & NOMOR SURAT THESIS ######
    path('admin/surat', views_admin.surat_list, name='admin_surat_list'),
    path('admin/surat/tambah', views_admin.surat_tambah, name='admin_surat_tambah'),
    path('admin/surat/<uuid:uuid>/edit', views_admin.surat_edit, name='admin_surat_edit'),
    path('admin/surat/<uuid:uuid>/hapus', views_admin.surat_hapus, name='admin_surat_hapus'),

    ###### KODE KLASIFIKASI SURAT ######
    path('admin/kode-surat', views_admin.kode_surat_list, name='admin_kode_surat_list'),
    path('admin/kode-surat/<uuid:uuid>/edit', views_admin.kode_surat_edit, name='admin_kode_surat_edit'),
    path('admin/kode-surat/<uuid:uuid>/hapus', views_admin.kode_surat_hapus, name='admin_kode_surat_hapus'),
    
    ###### PENGUNA/CLIENTS #######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),

    ###### E-COMMERCE KERANJANG & PESANAN PENGGUNA ######
    path('keranjang/', views_pengguna.cart_view, name='cart_view'),
    path('keranjang/tambah/<uuid:book_uuid>/', views_pengguna.cart_add, name='cart_add'),
    path('keranjang/tambah-course/<uuid:course_uuid>/', views_pengguna.cart_add_course, name='cart_add_course'),
    path('keranjang/update/<uuid:item_id>/', views_pengguna.cart_update, name='cart_update'),
    path('keranjang/hapus/<uuid:item_id>/', views_pengguna.cart_remove, name='cart_remove'),
    path('checkout/', views_pengguna.checkout_view, name='checkout'),
    path('pesanan/', views_pengguna.pesanan_list, name='pesanan_list'),
    path('pesanan/<str:order_number>/batalkan/', views_pengguna.batalkan_pesanan, name='batalkan_pesanan'),
    path('pesanan/<str:order_number>/', views_pengguna.pesanan_detail, name='pesanan_detail'),
    path('pesanan/<str:order_number>/upload-bukti/', views_pengguna.upload_bukti_transfer, name='upload_bukti_transfer'),
    path('pesanan/<str:order_number>/midtrans-token/', views_pengguna.get_order_snap_token, name='get_order_snap_token'),
    path('pesanan/<str:order_number>/sync-midtrans/', views_pengguna.sync_order_midtrans, name='sync_order_midtrans'),
    path('midtrans/notification/', views_pengguna.midtrans_notification, name='midtrans_notification'),

    ###### PELATIHAN SAYA (COURSE ENROLLED) ######
    path('pelatihan-saya/', views_pengguna.my_courses_list, name='my_courses'),
    path('pelatihan-saya/<uuid:order_item_id>/', views_pengguna.my_course_detail, name='my_course_detail'),
    path('pelatihan-saya/<uuid:order_item_id>/sertifikat/', views_pengguna.download_certificate, name='download_certificate'),

    ###### UMUM ######         
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),      
]