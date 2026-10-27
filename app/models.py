from decimal import Clamped
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import os
from django.conf import settings
from django.urls import reverse

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