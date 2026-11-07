from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from .models import (UserAdmin, Provinsi, BidangPenelitian, CategoryBooks, MediaBooks, Books, UserPengguna, Article, Category, Page, KerjaSama, HeroSlide, WebSetting, Course, CourseAgenda, JurnalMaster, LoaJurnal, NoSuratThesis, KodeSurat)


class formProfile(forms.ModelForm):
    class Meta:
        model = UserAdmin
        fields = [   
            'telp',
            'gender',
            'photo',
        ]
        widgets = {
            'gender': forms.Select(
                choices=[
                    ('Laki-laki', 'Laki-laki'),
                    ('Perempuan', 'Perempuan'),
                ],
                attrs={'class': 'form-control'}
            ),
            'telp': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CategoryBooksForm(forms.ModelForm):
    slug = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opsional (otomatis dari nama kategori jika kosong)'
        })
    )

    class Meta:
        model = CategoryBooks
        fields = ['nama_kategori', 'slug', 'deskripsi_kategori', 'aktif']
        widgets = {
            'nama_kategori': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Teknologi, Sains, Ekonomi',
                'required': True
            }),
            'deskripsi_kategori': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi singkat kategori (opsional)...'
            }),
            'aktif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        nama_kategori = self.cleaned_data.get('nama_kategori')
        if not slug and nama_kategori:
            slug = slugify(nama_kategori)
        elif not slug:
            slug = uuid.uuid4().hex[:8]
        
        if slug:
            qs = CategoryBooks.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug


class BooksForm(forms.ModelForm):
    slug = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opsional (otomatis dibuat jika kosong)'
        })
    )

    penulis = forms.ModelMultipleChoiceField(
        queryset=UserPengguna.objects.select_related('user').all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'id_penulis'
        }),
        required=False,
        label='Penulis (Bisa pilih satu atau lebih)'
    )

    editor = forms.ModelMultipleChoiceField(
        queryset=UserPengguna.objects.select_related('user').all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'id_editor'
        }),
        required=False,
        label='Editor (Bisa pilih satu atau lebih)'
    )

    kategori = forms.ModelChoiceField(
        queryset=CategoryBooks.objects.filter(aktif=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_kategori'
        }),
        required=False,
        empty_label='-- Pilih Kategori Buku --',
        label='Kategori Buku'
    )

    STATUS_CHOICES = [
        ('Tersedia', 'Tersedia'),
        ('Pre-Order', 'Pre-Order'),
        ('Habis', 'Habis'),
        ('Draft', 'Draft'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='Tersedia'
    )

    class Meta:
        model = Books
        fields = [
            'judul',
            'slug',
            'penulis',
            'editor',
            'kategori',
            'featured_image',
            'harga',
            'harga_potongan',
            'stok',
            'deskripsi',
            'bidang_ilmu',
            'isbn',
            'tahun',
            'ukuran',
            'halaman',
            'status',
        ]
        widgets = {
            'judul': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul Buku Lengkap',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opsional (otomatis dibuat jika kosong)'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_featured_image',
                'accept': 'image/*'
            }),
            'harga': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'min': '0',
                'placeholder': 'Contoh: 125000',
                'required': True
            }),
            'harga_potongan': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'min': '0',
                'placeholder': 'Contoh: 99000 (Harga diskon jika ada)'
            }),
            'stok': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Contoh: 50',
                'required': True
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control summernote-editor',
                'rows': 16,
                'placeholder': 'Sinopsis / deskripsi buku...',
                'required': True
            }),
            'bidang_ilmu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Sistem Informasi / Akuntansi'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 978-623-1234-56-7'
            }),
            'tahun': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 2025'
            }),
            'ukuran': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 15.5 x 23 cm'
            }),
            'halaman': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 250'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        judul = self.cleaned_data.get('judul')
        if not slug and judul:
            slug = slugify(judul)
        elif not slug:
            slug = uuid.uuid4().hex[:8]
        
        if slug:
            qs = Books.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug




class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'status', 'created_at', 'featured_image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul artikel / berita...',
                'required': 'required'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'created_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_featured_image',
                'accept': 'image/*'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control summernote-editor',
                'rows': 14,
                'placeholder': 'Tulis isi konten artikel di sini...'
            }),
        }


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'slug', 'featured_image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_title',
                'placeholder': 'Masukkan judul halaman (misal: Sejarah Lahirnya APBISDI, Visi Misi)...',
                'required': 'required'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_slug',
                'placeholder': 'Contoh: sejarah, visi-misi (kosongkan untuk generate otomatis dari judul)',
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_featured_image',
                'accept': 'image/*'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control summernote-editor',
                'rows': 16,
                'placeholder': 'Tulis isi halaman statis di sini...'
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kategori berita (misal: Pengumuman, Agenda, Riset)...',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi singkat kategori (opsional)...'
            }),
        }


class WebSettingForm(forms.ModelForm):
    class Meta:
        model = WebSetting
        fields = [
            'nama_web',
            'alamat',
            'no_telp',
            'email',
            'logo',
            'favicon',
            'link_maps',
            'link_instagram',
            'link_facebook',
            'link_tiktok',
            'link_youtube',
            'link_linkedin',
            'smtp_host',
            'smtp_port',
            'smtp_user',
            'smtp_password',
            'smtp_from_email',
        ]
        widgets = {
            'nama_web': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Asosiasi Profesi dan Pendidikan Bisnis Digital Indonesia (APBISDI)',
                'required': 'required'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alamat lengkap sekretariat / kantor pusat...',
                'required': 'required'
            }),
            'no_telp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: +62 812 2227 20568',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: sekretariat@apbisdi.or.id',
                'required': 'required'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_logo',
                'accept': 'image/*'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_favicon',
                'accept': 'image/*'
            }),
            'link_maps': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://maps.google.com/...'
            }),
            'link_instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/apbisdi'
            }),
            'link_facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/apbisdi'
            }),
            'link_tiktok': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tiktok.com/@apbisdi'
            }),
            'link_youtube': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/@apbisdi'
            }),
            'link_linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/company/apbisdi'
            }),
            'smtp_host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: smtp.gmail.com',
                'required': 'required'
            }),
            'smtp_port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 587',
                'required': 'required'
            }),
            'smtp_user': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: [EMAIL_ADDRESS]',
                'required': 'required'
            }),
            'smtp_password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: [PASSWORD]',
                'required': 'required'
            }),
            'smtp_from_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: [EMAIL_ADDRESS]',
                'required': 'required'
            }),
        }



class KerjaSamaForm(forms.ModelForm):
    class Meta:
        model = KerjaSama
        fields = ['nama_kerjasama', 'logo', 'link_website']
        widgets = {
            'nama_kerjasama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama instansi / mitra (misal: Bank Indonesia, Komdigi, OJK)...',
                'required': 'required'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_logo_kerjasama',
                'accept': 'image/*'
            }),
            'link_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.or.id (opsional)'
            }),
        }


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = [
            'judul', 'judul_highlight', 'badge_icon', 'badge_text',
            'deskripsi', 'tombol_teks', 'tombol_url',
            'banner', 'banner_url_eksternal', 'urutan',
        ]
        widgets = {
            'judul': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul utama slide (misal: Membangun Ekosistem...)',
                'required': 'required'
            }),
            'judul_highlight': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bagian judul yang diberi warna highlight (misal: Pendidikan & Bisnis Digital)',
            }),
            'badge_icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: ri-shield-flash-line (Remix Icon class)',
            }),
            'badge_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Asosiasi Resmi Nasional',
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deskripsi singkat yang tampil di bawah judul slide...',
                'required': 'required'
            }),
            'tombol_teks': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teks tombol CTA (misal: Pelajari Selengkapnya)',
            }),
            'tombol_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL tujuan tombol (misal: /daftar, #tata-cara)',
            }),
            'banner': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_banner_slide',
                'accept': 'image/*',
            }),
            'banner_url_eksternal': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://... (isi jika pakai banner dari URL eksternal, bukan upload)',
            }),
            'urutan': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
        }


class CourseForm(forms.ModelForm):
    slug = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opsional (otomatis dibuat dari nama kegiatan jika kosong)'
        }),
        label='Slug URL'
    )
    coaches = forms.ModelMultipleChoiceField(
        queryset=UserPengguna.objects.select_related('user').all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'id_coaches'
        }),
        required=False,
        label='Pembicara / Pelatih'
    )
    harga = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1000',
            'min': '0',
            'placeholder': 'Contoh: 150000'
        }),
        label='Harga Normal'
    )
    harga_potongan = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1000',
            'min': '0',
            'placeholder': 'Contoh: 99000 (Opsional)'
        }),
        label='Harga Diskon'
    )

    class Meta:
        model = Course
        fields = [
            'name', 'slug', 'course_type', 'format', 'coaches',
            'start_date', 'end_date', 'registration_deadline',
            'max_participants', 'meeting_url', 'thumbnail',
            'fee_type', 'price', 'harga', 'harga_potongan',
            'is_active', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kegiatan (misal: Pelatihan Analisis Data SPSS)',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opsional (otomatis dibuat dari nama kegiatan jika kosong)'
            }),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'end_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'registration_deadline': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kosongkan jika tidak dibatasi kuota',
                'min': '1'
            }),
            'meeting_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/... atau https://meet.google.com/...'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_thumbnail',
                'accept': 'image/*'
            }),
            'fee_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_fee_type'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0 jika gratis',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control summernote-editor',
                'rows': 8,
                'placeholder': 'Deskripsi kegiatan...'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name)
        elif not slug:
            slug = uuid.uuid4().hex[:8]

        if slug:
            qs = Course.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug

    def clean(self):
        cleaned_data = super().clean()
        fee_type = cleaned_data.get('fee_type')
        price = cleaned_data.get('price')
        harga = cleaned_data.get('harga')

        if fee_type == 'free':
            cleaned_data['price'] = 0
            if not harga:
                cleaned_data['harga'] = 0
        else:
            if not harga and price:
                cleaned_data['harga'] = price
            elif not price and harga:
                cleaned_data['price'] = harga
            elif not harga and not price:
                cleaned_data['harga'] = 0
                cleaned_data['price'] = 0

        return cleaned_data


class CourseAgendaForm(forms.ModelForm):
    class Meta:
        model = CourseAgenda
        fields = ['session_number', 'title', 'agenda_date', 'pengajar', 'jp_count']
        widgets = {
            'session_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 1',
                'min': '1'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul atau topik sesi...',
                'required': True
            }),
            'agenda_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}
            ),
            'pengajar': forms.Select(attrs={'class': 'form-control'}),
            'jp_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah JP (misal: 2)',
                'min': '1',
                'required': True
            }),
        }


class UserAccountEditForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nama Lengkap',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap Pengguna', 'required': True})
    )
    email = forms.EmailField(
        label='Alamat Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@domain.com', 'required': True})
    )
    is_active = forms.BooleanField(
        label='Akun Aktif',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'email', 'is_active']


class UserPenggunaEditForm(forms.ModelForm):
    jafung = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jabatan Fungsional --'),
            ('Tanpa Jabatan Fungsional', 'Tanpa Jabatan Fungsional'),
            ('Asisten Ahli', 'Asisten Ahli'),
            ('Lektor', 'Lektor'),
            ('Lektor Kepala', 'Lektor Kepala'),
            ('Guru Besar', 'Guru Besar'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Jabatan Fungsional'
    )
    gender = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jenis Kelamin --'),
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Jenis Kelamin'
    )
    provinsi_anggota = forms.ModelChoiceField(
        queryset=Provinsi.objects.filter(aktif=True).order_by('nama_provinsi'),
        empty_label='-- Pilih Provinsi --',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Provinsi Domisili'
    )
    bidang_penelitian = forms.ModelChoiceField(
        queryset=BidangPenelitian.objects.filter(aktif=True).order_by('nama_bidang'),
        empty_label='-- Pilih Bidang Penelitian --',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Bidang Penelitian'
    )

    class Meta:
        model = UserPengguna
        fields = [
            'telp', 'gender', 'nuptk', 'jafung', 'bidang_penelitian',
            'provinsi_anggota', 'alamat', 'photo',
            'link_sinta', 'link_scopus', 'link_google_scholar', 'link_orcid'
        ]
        widgets = {
            'telp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '081234567890'}),
            'nuptk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor NUPTK'}),
            'alamat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alamat tempat tinggal / instansi'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'link_sinta': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://sinta.kemdikbud.go.id/authors/detail?id=...'}),
            'link_scopus': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.scopus.com/authid/detail.uri?authorId=...'}),
            'link_google_scholar': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://scholar.google.com/citations?user=...'}),
            'link_orcid': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://orcid.org/0000-...'}),
        }


class UserAdminEditForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Jenis Kelamin'
    )

    class Meta:
        model = UserAdmin
        fields = ['telp', 'gender', 'photo']
        widgets = {
            'telp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '081234567890'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


# =====================================================================
#                      JURNAL MASTER & LOA JURNAL FORMS
# =====================================================================

class JurnalMasterForm(forms.ModelForm):
    class Meta:
        model = JurnalMaster
        fields = [
            'nama', 'singkatan', 'cover', 'issn', 'e_issn',
            'penerbit', 'url_jurnal', 'file_sk',
            'ttd_nama', 'ttd_jabatan', 'ttd_gambar',
            'indeks_1', 'indeks_2', 'indeks_3', 'indeks_4',
            'is_active',
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap jurnal ilmiah', 'required': True}),
            'singkatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: TheMas, JPT, dll'}),
            'cover': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'issn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2775-1234'}),
            'e_issn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2775-5678'}),
            'penerbit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lembaga / penerbit jurnal'}),
            'url_jurnal': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://jurnal.thesis.or.id/...'}),
            'file_sk': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'ttd_nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama pejabat penandatangan LOA'}),
            'ttd_jabatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Editor in Chief'}),
            'ttd_gambar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'indeks_1': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'indeks_2': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'indeks_3': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'indeks_4': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LoaJurnalForm(forms.ModelForm):
    no_surat = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Otomatis digenerate jika dikosongkan (contoh: 1/LOA/2026)'
        }),
        label='Nomor Surat'
    )
    nama_jurnal = forms.ModelChoiceField(
        queryset=JurnalMaster.objects.filter(is_active=True).order_by('nama'),
        empty_label='-- Pilih Jurnal --',
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        label='Nama Jurnal'
    )

    class Meta:
        model = LoaJurnal
        fields = [
            'no_surat', 'nama_jurnal', 'id_naskah', 'penulis',
            'judul_naskah', 'volume', 'nomor_jurnal',
            'periode_bulan', 'periode_tahun', 'status',
        ]
        widgets = {
            'id_naskah': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: #1042 / ART-2026-09', 'required': True}),
            'penulis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama penulis (bisa lebih dari satu, pisahkan dengan koma)', 'required': True}),
            'judul_naskah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Judul lengkap artikel / naskah ilmiah', 'required': True}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Vol'}),
            'nomor_jurnal': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'No'}),
            'periode_bulan': forms.Select(attrs={'class': 'form-control'}),
            'periode_tahun': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'placeholder': 'Tahun'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# =====================================================================
#                      SURAT THESIS & KODE SURAT FORMS
# =====================================================================

class KodeSuratForm(forms.ModelForm):
    class Meta:
        model = KodeSurat
        fields = ['jenis', 'kode']
        widgets = {
            'jenis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Surat Tugas, Surat Keputusan, Undangan', 'required': True}),
            'kode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: ST, SK, UND, PKM', 'required': True}),
        }


class NoSuratThesisForm(forms.ModelForm):
    class Meta:
        model = NoSuratThesis
        fields = ['tahun', 'nomor', 'perihal', 'tujuan', 'kode']
        widgets = {
            'tahun': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2026', 'required': True}),
            'nomor': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Contoh: 1, 2, dst', 'required': True}),
            'kode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kode klasifikasi surat (misal: ST / SK / LOA)', 'required': True}),
            'perihal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Perihal / Isi ringkas surat', 'required': True}),
            'tujuan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pihak tujuan / penerima surat', 'required': True}),
        }


