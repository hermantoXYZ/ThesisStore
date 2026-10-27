from django import forms
from django.utils.text import slugify
import uuid
from .models import (UserAdmin, Provinsi, CategoryBooks, MediaBooks, Books, UserPengguna)


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


