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
    provinsi_pengguna = models.ForeignKey(Provinsi, on_delete=models.SET_NULL, null=True, blank=True)
    jafung = models.CharField(max_length=100, null=True, blank=True)
    nuptk = models.CharField(max_length=20, null=True, blank=True, verbose_name='NUPTK')
    bidang_keahlian = models.ForeignKey(BidangPenelitian, on_delete=models.SET_NULL, null=True, blank=True)
    link_sinta = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link Sinta')
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
    featured_image = models.ImageField(upload_to=rename_featured_image, max_length=255, blank=True, null=True)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
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

    @property
    def harga_efektif(self):
        if self.harga_potongan and self.harga_potongan > 0:
            return self.harga_potongan
        return self.harga or 0

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


def rename_bukti_transfer(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    order_num = getattr(instance, 'order_number', 'order').replace('/', '_')
    return os.path.join('orders/bukti_transfer/', f"transfer_{order_num}_{timestamp}_{random_str}.{ext}")


class Course(models.Model):

    COURSE_TYPE_CHOICES = [
        ('training', 'Pelatihan'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
        ('workshop', 'Workshop'),
        ('bootcamp', 'Bootcamp'),
        ('other', 'Lainnya'),
    ]

    FORMAT_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline / Tatap Muka'),
        ('hybrid', 'Hybrid'),
    ]

    FEE_TYPE_CHOICES = [
        ('free', 'Gratis'),
        ('paid', 'Berbayar / Donasi (Tripay Payment Gateway)'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, verbose_name="Nama Kegiatan")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name="Slug URL")
    description = models.TextField(max_length=1000, verbose_name="Deskripsi")
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='training', verbose_name="Jenis Kegiatan")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='online', verbose_name="Format Pelaksanaan")
    coaches = models.ManyToManyField(UserPengguna, blank=True, related_name='coached_courses')
    start_date = models.DateField(null=True, blank=True, verbose_name="Tanggal Mulai", help_text="Tanggal pelaksanaan dimulai")
    end_date = models.DateField(null=True, blank=True, verbose_name="Tanggal Selesai", help_text="Tanggal pelaksanaan berakhir")
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    harga_potongan = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kuota Peserta", help_text="Kosongkan jika tidak ada batas peserta")
    registration_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Batas Pendaftaran", help_text="Batas akhir pendaftaran peserta")
    meeting_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link Meeting", help_text="Link Zoom / Google Meet (untuk online/hybrid)")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True, verbose_name="Thumbnail", help_text="Gambar sampul kegiatan")
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='free', verbose_name="Tipe Biaya")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Nominal Biaya / Donasi (Rp)", help_text="Isi 0 jika gratis")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_course_type_display()})"

    def get_absolute_url(self):
        if self.slug:
            return reverse('course_detail', kwargs={'slug': self.slug})
        return reverse('course_detail', kwargs={'slug': str(self.uuid)})

    @property
    def formatted_price(self):
        try:
            return f"{int(self.price):,}".replace(",", ".")
        except (ValueError, TypeError):
            return "0"

    @property
    def persentase_diskon(self):
        if self.harga and self.harga > 0 and self.harga_potongan and self.harga_potongan < self.harga:
            return int(round(((self.harga - self.harga_potongan) / self.harga) * 100))
        return 0

    @property
    def harga_efektif(self):
        if self.harga_potongan and self.harga_potongan > 0:
            return self.harga_potongan
        return self.harga or 0



class CourseAgenda(models.Model):
    course = models.ForeignKey(Course, related_name='agendas', on_delete=models.CASCADE)
    session_number = models.PositiveSmallIntegerField(null=True, blank=True) 
    title = models.CharField(max_length=255)
    agenda_date = models.DateTimeField(null=True, blank=False, help_text="Tanggal & jam pelaksanaan")
    pengajar = models.ForeignKey(UserPengguna, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_agendas', help_text="Dosen pengampu sesi ini (bisa berbeda dari pembuat)")
    jp_count = models.PositiveSmallIntegerField(null=True, blank=False, verbose_name="Jumlah JP", help_text="Jumlah Jam Pelajaran (JP) pada sesi ini")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['session_number', 'agenda_date']
        unique_together = [('course', 'session_number')]  # Satu nomor sesi per course

    def __str__(self):
        if self.session_number:
            return f"{self.course.name} - Sesi {self.session_number}: {self.title}"
        return f"{self.course.name} - {self.title}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Keranjang Belanja'
        verbose_name_plural = 'Keranjang Belanja'

    def __str__(self):
        return f"Keranjang {self.user.username}"

    def get_total_price(self):
        return sum((item.get_subtotal() or 0) for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        title = self.course.name if self.course else (self.book.judul if self.book else 'Item')
        return f"{self.quantity}x {title}"

    def get_price(self):
        if self.course:
            return self.course.harga_efektif
        if self.book:
            return self.book.harga_efektif
        return 0

    def get_subtotal(self):
        return (self.get_price() or 0) * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Menunggu Pembayaran'),
        ('paid', 'Menunggu Konfirmasi'),
        ('processing', 'Sedang Diproses'),
        ('shipped', 'Dalam Pengiriman'),
        ('delivered', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Data Penerima & Pengiriman
    nama_penerima = models.CharField(max_length=150)
    no_hp = models.CharField(max_length=25)
    provinsi = models.CharField(max_length=100, blank=True, null=True)
    kota = models.CharField(max_length=100, blank=True, null=True)
    kode_pos = models.CharField(max_length=10, blank=True, null=True)
    alamat_pengiriman = models.TextField()
    catatan = models.TextField(blank=True, null=True)

    # Rincian Biaya
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ongkir = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_harga = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Pembayaran & Ekspedisi
    metode_pembayaran = models.CharField(max_length=50, default='Transfer Bank')
    bukti_transfer = models.FileField(upload_to=rename_bukti_transfer, blank=True, null=True)
    nomor_resi = models.CharField(max_length=100, blank=True, null=True)
    kurir = models.CharField(max_length=50, blank=True, null=True)

    # Integrasi Midtrans Payment Gateway
    snap_token = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.nama_penerima}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Books, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    judul_buku = models.CharField(max_length=255)
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)


    def __str__(self):
        return f"{self.quantity}x {self.judul_buku}"

def rename_jurnal_cover(instance, filename):
    ext = filename.split('.')[-1]
    name_clean = slugify(instance.nama)[:50].replace("-", "_")
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"jurnal_{name_clean}_{timestamp}.{ext}"
    return os.path.join('jurnal/covers/', new_filename)

def rename_jurnal_ttd(instance, filename):
    ext = filename.split('.')[-1]
    name_clean = slugify(instance.nama)[:50].replace("-", "_")
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"ttd_{name_clean}_{timestamp}.{ext}"
    return os.path.join('jurnal/ttd/', new_filename)

def rename_jurnal_index(instance, filename):
    ext = filename.split('.')[-1]
    name_clean = slugify(instance.nama)[:50].replace("-", "_")
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"indeks_{name_clean}_{timestamp}.{ext}"
    return os.path.join('jurnal/indeks/', new_filename)


class JurnalMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255, verbose_name="Nama Jurnal", unique=True)
    singkatan = models.CharField(max_length=50, verbose_name="Singkatan Jurnal", blank=True, null=True, help_text="Contoh: TheMas, JPT, dll. Digunakan untuk nomor surat.")
    cover = models.ImageField(upload_to=rename_jurnal_cover, blank=True, null=True, verbose_name="Cover Jurnal")
    issn = models.CharField(max_length=30, blank=True, null=True, verbose_name="ISSN")
    e_issn = models.CharField(max_length=30, blank=True, null=True, verbose_name="E-ISSN")
    penerbit = models.CharField(max_length=255, blank=True, null=True, verbose_name="Penerbit")
    url_jurnal = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL Jurnal")
    file_sk = models.FileField(upload_to='jurnal_sk/', blank=True, null=True, verbose_name="File SK (Surat Keputusan Jurnal)")
    ttd_nama = models.CharField(max_length=255, verbose_name="Nama Penandatangan TTD", blank=True, null=True)
    ttd_jabatan = models.CharField(max_length=255, verbose_name="Jabatan Penandatangan TTD", blank=True, null=True)
    ttd_gambar = models.ImageField(upload_to=rename_jurnal_ttd, blank=True, null=True, verbose_name="Gambar TTD")
    indeks_1 = models.ImageField(upload_to=rename_jurnal_index, blank=True, null=True, verbose_name="Logo Indeksasi 1")
    indeks_2 = models.ImageField(upload_to=rename_jurnal_index, blank=True, null=True, verbose_name="Logo Indeksasi 2")
    indeks_3 = models.ImageField(upload_to=rename_jurnal_index, blank=True, null=True, verbose_name="Logo Indeksasi 3")
    indeks_4 = models.ImageField(upload_to=rename_jurnal_index, blank=True, null=True, verbose_name="Logo Indeksasi 4")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nama']
        verbose_name = "Master Jurnal"
        verbose_name_plural = "Master Jurnal"

    def __str__(self):
        issn_info = f" (ISSN: {self.issn})" if self.issn else ""
        return f"{self.nama}{issn_info}"

class LoaJurnal(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    BULAN_CHOICES = [
        ('Januari', 'Januari'),
        ('Februari', 'Februari'),
        ('Maret', 'Maret'),
        ('April', 'April'),
        ('Mei', 'Mei'),
        ('Juni', 'Juni'),
        ('Juli', 'Juli'),
        ('Agustus', 'Agustus'),
        ('September', 'September'),
        ('Oktober', 'Oktober'),
        ('November', 'November'),
        ('Desember', 'Desember'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    no_surat = models.CharField(max_length=50, verbose_name="Nomor Surat")
    judul_naskah = models.CharField(max_length=500, verbose_name="Judul Naskah")
    penulis = models.CharField(max_length=255, verbose_name="Penulis")
    id_naskah = models.CharField(max_length=100, verbose_name="ID Naskah")
    nama_jurnal = models.ForeignKey(JurnalMaster, on_delete=models.SET_NULL, null=True, blank=True,related_name='loa_jurnals', verbose_name="Nama Jurnal")
    volume = models.PositiveIntegerField(default=1, verbose_name="Volume")
    nomor_jurnal = models.PositiveIntegerField(default=1, verbose_name="Nomor Jurnal")
    periode_bulan = models.CharField(max_length=20, choices=BULAN_CHOICES, default='Juli', verbose_name="Bulan Terbit")
    periode_tahun = models.PositiveIntegerField(verbose_name="Tahun Terbit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted', verbose_name="Status LOA")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name='loa_jurnals', verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "LOA Jurnal"
        verbose_name_plural = "LOA Jurnal"

    def __str__(self):
        return f"LOA: {self.judul_naskah} – {self.penulis} ({self.get_status_display()})"

    @property
    def nomor_surat_formatted(self):
        return self.no_surat or "-"

class NoSuratThesis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_in = models.DateTimeField(auto_now_add=True)
    adminp = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="nosuratth_admin")
    tahun = models.CharField(max_length=5, blank=False, null=False)
    nomor = models.IntegerField(blank=False, null=False)
    perihal = models.CharField(max_length=255, blank=False, null=False)
    tujuan = models.CharField(max_length=255, blank=False, null=False)
    kode = models.CharField(max_length=50, blank=False, null=False)

class KodeSurat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jenis = models.CharField(max_length=100, blank=False, null=False)
    kode = models.CharField(max_length=50, blank=False, null=False)
    def __str__(self):
        return f"{self.jenis} - {self.kode}"


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