
from django import forms
from datetime import date
from .models import UserPengguna, Provinsi, BidangPenelitian

class formProfile(forms.ModelForm):
    jafung = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jabatan Fungsional --'),
            ('Tanpa Jabatan Fungsional', 'Tanpa Jabatan Fungsional'),
            ('Asisten Ahli', 'Asisten Ahli'),
            ('Lektor', 'Lektor'),
        ('Lektor Kepala', 'Lektor Kepala'),
        ('Guru Besar', 'Guru Besar'),
    ],
    widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'id_jafung'
    }),
    required=False
    )

    gender = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jenis Kelamin --'),
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_gender'}),
        required=True
    )

    provinsi_pengguna = forms.ModelChoiceField(
        queryset=Provinsi.objects.filter(aktif=True).order_by('nama_provinsi'),
        empty_label='-- Pilih Provinsi Domisili Kampus --',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_provinsi_pengguna'}),
        required=False
    )

    bidang_keahlian = forms.ModelChoiceField(
        queryset=BidangPenelitian.objects.filter(aktif=True).order_by('nama_bidang'),
        empty_label='-- Pilih Bidang Keahlian --',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_bidang_keahlian'}),
        required=False
    )

    class Meta:
        model = UserPengguna
        fields = [
            'telp',
            'gender',
            'nuptk',
            'jafung',
            'bidang_keahlian',
            'alamat',
            'provinsi_pengguna',
            'photo',
            'link_sinta',
            'link_scopus',
            'link_google_scholar',
            'link_orcid',
        ]
        widgets = {
            'telp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 081234567890', 'required': True}),
            'nuptk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor NUPTK (opsional)'}),
            'alamat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alamat instansi / tempat tinggal'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'link_sinta': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: https://sinta.kemdikbud.go.id/authors/detail?id=123456'}),
            'link_scopus': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: https://www.scopus.com/authid/detail.uri?authorId=123456'}),
            'link_google_scholar': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: https://scholar.google.com/citations?user=123456'}),
            'link_orcid': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: https://orcid.org/0000-0001-2345-6789'}),
        }


