from django.urls import path
from . import views
from . import views_admin
from . import views_pengguna
from . import views_admin_set
from . import views_narasumber
from .view_print import print_loa_jurnal, print_sertifikat_narasumber, print_sertifikat_pengguna

urlpatterns = [
    ###### ADMIN: KEANGGOTAAN INDIVIDU & PENGATURAN WEB ######
    path('profile/admin', views_admin_set.profile_admin, name='profile_admin'),
    path('user/list', views_admin_set.user_list, name='user_list'),
    path('user/edit/<str:id>/<str:role>/', views_admin_set.user_edit, name='user_edit'),
    path('admin/web-setting', views_admin.web_setting_view, name='admin_web_setting'),

    ###### ADMIN: KATEGORI & MASTER BUKU ######
    path('buku/kategori/', views_admin.kategori_buku_list, name='kategori_buku_list'),
    path('buku/kategori/tambah/', views_admin.kategori_buku_tambah, name='kategori_buku_tambah'),
    path('buku/kategori/edit/<uuid:uuid>/', views_admin.kategori_buku_edit, name='kategori_buku_edit'),
    path('buku/kategori/hapus/<uuid:uuid>/', views_admin.kategori_buku_hapus, name='kategori_buku_hapus'),
    path('buku/', views_admin.buku_list, name='buku_list'),
    path('buku/tambah/', views_admin.buku_tambah, name='buku_tambah'),
    path('buku/edit/<uuid:uuid>/', views_admin.buku_edit, name='buku_edit'),
    path('buku/hapus/<uuid:uuid>/', views_admin.buku_hapus, name='buku_hapus'),
    path('buku/<uuid:book_uuid>/media/hapus/<uuid:media_uuid>/', views_admin.buku_media_hapus, name='buku_media_hapus'),

    ###### ADMIN: PESANAN BUKU & COURSE ######
    path('admin/pesanan/buku/', views_admin.admin_order_list_buku, name='admin_order_list'),
    path('admin/pesanan/buku/<str:order_number>/', views_admin.admin_order_detail_buku, name='admin_order_detail'),
    path('admin/pesanan/course/', views_admin.admin_order_list_course, name='admin_order_list_course'),
    path('admin/pesanan/course/<str:order_number>/', views_admin.admin_order_detail_course, name='admin_order_detail_course'),

    ###### ADMIN: ARTIKEL / BERITA & KATEGORI ######
    path('admin/article', views_admin.article_list, name='admin_article_list'),
    path('admin/article/create', views_admin.article_create, name='admin_article_create'),
    path('admin/article/<uuid:article_id>/edit', views_admin.article_edit, name='admin_article_edit'),
    path('admin/article/<uuid:article_id>/delete', views_admin.article_delete, name='admin_article_delete'),
    path('admin/article/dokumentasi/<uuid:foto_id>/delete', views_admin.delete_dokumentasi_article, name='admin_delete_dokumentasi_article'),
    path('admin/category', views_admin.category_list, name='admin_category_list'),
    path('admin/category/<uuid:category_id>/delete', views_admin.category_delete, name='admin_category_delete'),

    ###### ADMIN: HALAMAN (PAGE), MITRA & HERO SLIDES ######
    path('admin/page', views_admin.page_list, name='admin_page_list'),
    path('admin/page/create', views_admin.page_create, name='admin_page_create'),
    path('admin/page/<uuid:page_id>/edit', views_admin.page_edit, name='admin_page_edit'),
    path('admin/page/<uuid:page_id>/delete', views_admin.page_delete, name='admin_page_delete'),
    path('admin/page/dokumentasi/<uuid:foto_id>/delete', views_admin.delete_dokumentasi_page, name='admin_delete_dokumentasi_page'),
    path('admin/kerjasama', views_admin.kerjasama_list, name='admin_kerjasama_list'),
    path('admin/kerjasama/<uuid:kerjasama_id>/edit', views_admin.kerjasama_edit, name='admin_kerjasama_edit'),
    path('admin/kerjasama/<uuid:kerjasama_id>/delete', views_admin.kerjasama_delete, name='admin_kerjasama_delete'),
    path('admin/hero-slides', views_admin.hero_slide_list, name='admin_hero_slide_list'),
    path('admin/hero-slides/create', views_admin.hero_slide_create, name='admin_hero_slide_create'),
    path('admin/hero-slides/<uuid:slide_id>/edit', views_admin.hero_slide_edit, name='admin_hero_slide_edit'),
    path('admin/hero-slides/<uuid:slide_id>/delete', views_admin.hero_slide_delete, name='admin_hero_slide_delete'),

    ###### ADMIN: KELOLA COURSE, AGENDA, MATERI, QUIZ & KUESIONER ######
    path('admin/course', views_admin.course_list, name='admin_course_list'),
    path('admin/course/create', views_admin.course_create, name='admin_course_create'),
    path('admin/course/<uuid:uuid>/edit', views_admin.course_edit, name='admin_course_edit'),
    path('admin/course/<uuid:uuid>/delete', views_admin.course_delete, name='admin_course_delete'),
    path('admin/course/<uuid:course_uuid>/agenda/add', views_admin.course_agenda_add, name='admin_course_agenda_add'),
    path('admin/course/agenda/<uuid:agenda_uuid>/edit/', views_admin.course_agenda_edit, name='admin_course_agenda_edit'),
    path('admin/course/agenda/<uuid:agenda_uuid>/delete/', views_admin.course_agenda_delete, name='admin_course_agenda_delete'),
    path('admin/course/agenda/<uuid:agenda_uuid>/materi/', views_admin.admin_agenda_material, name='admin_agenda_material'),
    path('admin/course/materi/<uuid:materi_id>/edit/', views_admin.admin_agenda_material_edit, name='admin_agenda_material_edit'),
    path('admin/course/materi/<uuid:materi_id>/delete/', views_admin.admin_agenda_material_delete, name='admin_agenda_material_delete'),
    path('admin/course/<uuid:course_uuid>/agenda/', views_admin.admin_course_agenda_manage, name='admin_course_agenda_manage'),
    path('admin/course/agenda/<uuid:agenda_uuid>/quiz/', views_admin.admin_agenda_quiz, name='admin_agenda_quiz'),
    path('admin/course/<uuid:course_uuid>/survey/', views_admin.admin_course_survey, name='admin_course_survey'),
    path('admin/course/<uuid:course_uuid>/survey/question/add/', views_admin.admin_survey_question_add, name='admin_survey_question_add'),
    path('admin/survey/question/<uuid:question_id>/edit/', views_admin.admin_survey_question_edit, name='admin_survey_question_edit'),
    path('admin/survey/question/<uuid:question_id>/delete/', views_admin.admin_survey_question_delete, name='admin_survey_question_delete'),
    path('admin/course/<uuid:course_uuid>/survey/export/', views_admin.admin_survey_export_csv, name='admin_survey_export_csv'),

    ###### ADMIN: ENROLLMENT / PESERTA COURSE ######
    path('admin/course/<uuid:course_uuid>/enrollment/', views_admin.admin_enrollment_list, name='admin_enrollment_list'),
    path('admin/enrollment/create', views_admin.admin_enrollment_create, name='admin_enrollment_create'),
    path('admin/enrollment/<uuid:enrollment_id>/status', views_admin.admin_enrollment_update_status, name='admin_enrollment_update_status'),

    ###### ADMIN: JURNAL ILMIAH, LOA & PENDAFTARAN REVIEWER ######
    path('admin/jurnal', views_admin.jurnal_list, name='admin_jurnal_list'),
    path('admin/jurnal/tambah', views_admin.jurnal_tambah, name='admin_jurnal_tambah'),
    path('admin/jurnal/<uuid:uuid>/edit', views_admin.jurnal_edit, name='admin_jurnal_edit'),
    path('admin/jurnal/<uuid:uuid>/hapus', views_admin.jurnal_hapus, name='admin_jurnal_hapus'),
    path('admin/loa', views_admin.loa_jurnal_list, name='admin_loa_jurnal_list'),
    path('admin/loa/tambah', views_admin.loa_jurnal_tambah, name='admin_loa_jurnal_tambah'),
    path('admin/loa/<uuid:uuid>/edit', views_admin.loa_jurnal_edit, name='admin_loa_jurnal_edit'),
    path('admin/loa/<uuid:uuid>/hapus', views_admin.loa_jurnal_hapus, name='admin_loa_jurnal_hapus'),
    path('admin/loa/<uuid:uuid>/print', print_loa_jurnal.loa_jurnal_print, name='admin_loa_jurnal_print'),
    path('loa/<uuid:uuid>/print', print_loa_jurnal.loa_jurnal_print, name='loa_jurnal_print'),
    path('admin/reviewer/', views_admin.reviewer_application_list, name='admin_reviewer_list'),
    path('admin/reviewer/add/', views_admin.admin_reviewer_add, name='admin_reviewer_add'),
    path('admin/reviewer/<uuid:app_id>/', views_admin.reviewer_application_detail, name='admin_reviewer_detail'),

    ###### ADMIN: TATA USAHA, NOMOR SURAT & KLASIFIKASI ######
    path('admin/surat', views_admin.surat_list, name='admin_surat_list'),
    path('admin/surat/tambah', views_admin.surat_tambah, name='admin_surat_tambah'),
    path('admin/surat/<uuid:uuid>/edit', views_admin.surat_edit, name='admin_surat_edit'),
    path('admin/surat/<uuid:uuid>/hapus', views_admin.surat_hapus, name='admin_surat_hapus'),
    path('admin/kode-surat', views_admin.kode_surat_list, name='admin_kode_surat_list'),
    path('admin/kode-surat/<uuid:uuid>/edit', views_admin.kode_surat_edit, name='admin_kode_surat_edit'),
    path('admin/kode-surat/<uuid:uuid>/hapus', views_admin.kode_surat_hapus, name='admin_kode_surat_hapus'),

    ###### PENGGUNA: PROFIL, KERANJANG & PEMBAYARAN ######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),
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
    path('journal/apply/', views_pengguna.apply_journal, name='apply_journal'),

    ###### PENGGUNA: NARASUMBER & PELATIHAN SAYA (ACADEMY) ######
    path('narasumber/', views_pengguna.my_narasumber_list, name='my_narasumber'),
    path('narasumber/<uuid:course_uuid>/', views_pengguna.my_narasumber_detail, name='my_narasumber_detail'),
    path('narasumber/agenda/<uuid:agenda_uuid>/materi/add/', views_narasumber.narasumber_materi_add, name='narasumber_materi_add'),
    path('narasumber/materi/<uuid:materi_id>/edit/', views_pengguna.narasumber_materi_edit, name='narasumber_materi_edit'),
    path('narasumber/materi/<uuid:materi_id>/hapus/', views_pengguna.narasumber_materi_delete, name='narasumber_materi_delete'),
    path('narasumber/agenda/<uuid:agenda_uuid>/quiz/', views_narasumber.narasumber_agenda_quiz, name='narasumber_agenda_quiz'),
    path('academy/', views_pengguna.my_courses_list, name='my_courses'),
    path('academy/<uuid:order_item_id>/', views_pengguna.my_course_detail, name='my_course_detail'),
    path('academy/<uuid:order_item_id>/quiz/<uuid:quiz_id>/', views_pengguna.my_course_quiz, name='my_course_quiz'),
    path('academy/<uuid:order_item_id>/kuesioner/', views_pengguna.my_course_survey, name='my_course_survey'),
    path('print/sertifikat/peserta/<uuid:order_item_id>/', print_sertifikat_pengguna.sertifikat_pengguna, name='sertifikat_pengguna'),
    path('print/sertifikat/narasumber/<uuid:order_item_id>/', print_sertifikat_narasumber.sertifikat_narasumber, name='sertifikat_narasumber'),

    ###### UMUM ######
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),
]