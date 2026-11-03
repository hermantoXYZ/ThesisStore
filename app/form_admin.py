from django import forms
from django.utils.text import slugify
import uuid
from .models import (UserAdmin, Provinsi, CategoryBooks, MediaBooks, Books, UserPengguna, Article, Category, Page, KerjaSama, HeroSlide, WebSetting)


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
            'nama_organisasi': forms.TextInput(attrs={
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
