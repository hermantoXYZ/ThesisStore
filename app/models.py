from decimal import Clamped
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import os
from django.conf import settings
from django.urls import reverse

from django.utils.text import slugify
from datetime import date

User.add_to_class("__str__", lambda self: f"{self.username} - {self.first_name}")

class Provinsi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_provinsi = models.CharField(max_length=100, unique=True, verbose_name='Nama Provinsi')
    aktif = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Provinsi'
        verbose_name_plural = 'Provinsi'
        ordering = ['nama_provinsi']

    def __str__(self):
        return f"{self.nama_provinsi}"

def rename_photo_anggota(instance, filename):
    ext = filename.split('.')[-1]
    username = instance.user.username
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{username}_{timestamp}.{ext}"
    return os.path.join('img_profile/anggota/', new_filename)

class BidangPenelitian(models.Model):
    nama_bidang = models.CharField(max_length=100, unique=True, verbose_name='Nama Bidang')
    aktif = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Bidang Penelitian'
        verbose_name_plural = 'Bidang Penelitian'
        ordering = ['nama_bidang']

    def __str__(self):
        return f"{self.nama_bidang}"

class UserPengguna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="anggota")
    telp = models.CharField(max_length=15)
    gender = models.CharField(max_length=15, null=True, blank=True, choices=[
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ]) 
    alamat = models.CharField(max_length=50, null=True, blank=True)
    photo = models.ImageField(upload_to=rename_photo_anggota, null=True, blank=True)
    provinsi_anggota = models.ForeignKey(Provinsi, on_delete=models.SET_NULL, null=True, blank=True)
    jafung = models.CharField(max_length=100, null=True, blank=True)
    nuptk = models.CharField(max_length=20, null=True, blank=True, verbose_name='NUPTK')
    bidang_penelitian = models.ForeignKey(BidangPenelitian, on_delete=models.SET_NULL, null=True, blank=True)
    link_sinta = models.URLField(max_length=200, verbose_name='Link Sinta')
    link_scopus = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link Scopus')
    link_google_scholar = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link Google Scholar')
    link_orcid = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link ORCID')


    class Meta:
        verbose_name = 'Anggota'
        verbose_name_plural = 'Anggota'

    def save(self, *args, **kwargs):
        try:
            old_instance = UserPengguna.objects.get(pk=self.pk)
            if old_instance.photo and old_instance.photo != self.photo:
                old_photo_path = os.path.join(
                    settings.MEDIA_ROOT,
                    old_instance.photo.name
                )
                if os.path.isfile(old_photo_path):
                    os.remove(old_photo_path)
        except UserPengguna.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} ({self.user.username})" if self.user.first_name else self.user.username

def rename_photo_admin(instance, filename):
    ext = filename.split('.')[-1]
    username = instance.username
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S') 
    new_filename = f"{username}_{timestamp}.{ext}"
    return os.path.join('img_profile/admin/', new_filename)  


class UserAdmin(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, to_field="username", primary_key=True)
    telp = models.CharField(max_length=15)
    gender = models.CharField(max_length=15, choices=[
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ])
    photo = models.ImageField(upload_to=rename_photo_admin)

    def save(self, *args, **kwargs):
        try:
            old_instance = UserAdmin.objects.get(pk=self.pk)
            if old_instance.photo and old_instance.photo != self.photo:
                old_photo_path = os.path.join(settings.MEDIA_ROOT, old_instance.photo.name)
                if os.path.isfile(old_photo_path):
                    os.remove(old_photo_path)
        except UserAdmin.DoesNotExist:
            pass  

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

####### PRODUK ########

class CategoryBooks(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    nama_kategori = models.CharField(max_length=100)
    deskripsi_kategori = models.TextField(null=True, blank=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'CategoryBooks'
        verbose_name_plural = 'CategoryBooks'
        ordering = ['nama_kategori']

    def __str__(self):
        return f"{self.nama_kategori}"
 
def rename_featured_image(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    return os.path.join('books/featured_image/', f"featured_image_{timestamp}_{random_str}.{ext}")

class Books(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    judul = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, max_length=200)
    penulis = models.ManyToManyField(UserPengguna, blank=True, related_name='penulis_buku')
    editor = models.ManyToManyField(UserPengguna, blank=True, related_name='editor_buku')
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    featured_image = models.ImageField(upload_to=rename_featured_image, max_length=255, blank=True, null=True)
    harga_potongan = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stok = models.IntegerField()
    deskripsi = models.TextField()
    kategori = models.ForeignKey(CategoryBooks, on_delete=models.SET_NULL, null=True, blank=True)
    bidang_ilmu = models.CharField(max_length=100, null=True, blank=True)
    isbn = models.CharField(max_length=20, null=True, blank=True)
    tahun = models.CharField(max_length=4, null=True, blank=True)
    ukuran = models.CharField(max_length=50, null=True, blank=True)
    halaman = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Books'
        verbose_name_plural = 'Books'
        ordering = ['judul']

    def __str__(self):
        return self.judul 

    def get_absolute_url(self):
        if self.kategori and self.kategori.slug:
            return reverse('buku_detail', kwargs={'kategori_slug': self.kategori.slug, 'slug': self.slug})
        return reverse('buku_detail_simple', kwargs={'slug': self.slug})

    @property
    def persentase_diskon(self):
        if self.harga and self.harga > 0 and self.harga_potongan and self.harga_potongan < self.harga:
            return int(round(((self.harga - self.harga_potongan) / self.harga) * 100))
        return 0

def rename_media_books(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    return os.path.join('books/media/', f"media_book_{timestamp}_{random_str}.{ext}")


class MediaBooks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='media_buku')
    media = models.ImageField(upload_to=rename_media_books, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Media Buku'
        verbose_name_plural = 'Media Buku'
        ordering = ['created_at']

    def __str__(self):
        return f"Media: {self.book.judul}"

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

def rename_featured_image(instance, filename):
    ext = filename.split('.')[-1]
    title_slug = slugify(instance.title)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{title_slug}_{timestamp}.{ext}"
    return os.path.join('articles/featured_images/', new_filename)

class Article(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(upload_to=rename_featured_image, blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def rename_dokumentasi_article(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    return os.path.join('articles/dokumentasi/', f"doc_art_{timestamp}_{random_str}.{ext}")


class DokumentasiArticle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='dokumentasi_foto')
    foto = models.ImageField(upload_to=rename_dokumentasi_article)
    caption = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dokumentasi Artikel'
        verbose_name_plural = 'Dokumentasi Artikel'
        ordering = ['created_at']

    def __str__(self):
        return f"Dokumentasi: {self.article.title}"


def rename_page_hero_image(instance, filename):
    ext = filename.split('.')[-1]
    title_slug = slugify(instance.title)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{title_slug}_{timestamp}.{ext}"
    return os.path.join('pages/hero_images/', new_filename)


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pages')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to=rename_page_hero_image, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def rename_dokumentasi_page(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    return os.path.join('pages/dokumentasi/', f"doc_page_{timestamp}_{random_str}.{ext}")


class DokumentasiPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='dokumentasi_foto')
    foto = models.ImageField(upload_to=rename_dokumentasi_page)
    caption = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Dokumentasi Halaman'
        verbose_name_plural = 'Dokumentasi Halaman'
        ordering = ['created_at']

    def __str__(self):
        return f"Dokumentasi: {self.page.title}"


class WebSetting(models.Model):
    nama_web = models.CharField(max_length=200)
    alamat = models.TextField()
    no_telp = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='web_setting/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='web_setting/favicon/', blank=True, null=True)
    link_instagram = models.URLField(blank=True, null=True)
    link_facebook = models.URLField(blank=True, null=True)
    link_tiktok = models.URLField(blank=True, null=True)
    link_youtube = models.URLField(blank=True, null=True)
    link_linkedin = models.URLField(blank=True, null=True)
    link_maps = models.URLField(blank=True, null=True)
    smtp_host = models.CharField(max_length=100, default='smtp.gmail.com', verbose_name='SMTP Host')
    smtp_port = models.PositiveIntegerField(default=587, verbose_name='SMTP Port')
    smtp_user = models.EmailField(blank=True, null=True, verbose_name='Email Pengirim (SMTP User)')
    smtp_password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Password Aplikasi / SMTP Password')
    smtp_from_email = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nama & Email Pengirim (From)')

    class Meta:
        verbose_name = 'Pengaturan Website'
        verbose_name_plural = 'Pengaturan Website'

    def __str__(self):
        return self.nama_web
    

class KerjaSama(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_kerjasama = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='kerja_sama/logo/', blank=True, null=True)
    link_website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Kerja Sama'
        verbose_name_plural = 'Kerja Sama'
        ordering = ['-created_at']

    def __str__(self):
        return self.nama_kerjasama


def rename_hero_slide_banner(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    new_filename = f"slide_{timestamp}_{random_str}.{ext}"
    return os.path.join('hero_slides/', new_filename)


class HeroSlide(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=200, verbose_name='Judul Slide')
    judul_highlight = models.CharField(max_length=200, blank=True, null=True, verbose_name='Judul (Bagian Highlight/Warna)')
    badge_icon = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ikon Badge (Remix Icon class)', help_text='Contoh: ri-shield-flash-line')
    badge_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Teks Badge')
    deskripsi = models.TextField(verbose_name='Deskripsi Slide')
    tombol_teks = models.CharField(max_length=100, default='Pelajari Lebih Lanjut', verbose_name='Teks Tombol CTA')
    tombol_url = models.CharField(max_length=200, default='#', verbose_name='URL Tombol CTA', help_text='Contoh: /daftar, #section-id, atau URL lengkap')
    banner = models.ImageField(upload_to=rename_hero_slide_banner, blank=True, null=True, verbose_name='Gambar Banner Slide', help_text='Upload gambar atau GIF banner untuk slide ini')
    banner_url_eksternal = models.URLField(blank=True, null=True, verbose_name='URL Banner Eksternal', help_text='Isi jika menggunakan banner dari URL eksternal (misal GIF dari server lain). Kosongkan jika upload file.')
    urutan = models.PositiveIntegerField(default=0, verbose_name='Urutan Tampil')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
        ordering = ['urutan', 'created_at']

    def get_banner_url(self):
        if self.banner_url_eksternal:
            return self.banner_url_eksternal
        if self.banner:
            return self.banner.url
        return ''

    def __str__(self):
        return f"{self.urutan}. {self.judul}"
