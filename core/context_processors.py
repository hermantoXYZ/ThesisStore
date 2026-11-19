import os
from django.conf import settings


from app.models import WebSetting


# myapp/context_processors.py
def web_name(request):
    setting = None
    try:
        setting = WebSetting.objects.first()
    except Exception:
        pass

    nama_web = setting.nama_web if setting and setting.nama_web else 'Thesis Edukasi Nusantara'
    alamat = setting.alamat if setting and setting.alamat else 'Kompleks Mahkota Panggung Blok F No. 76. Desa Panggung, Kec. Pelaihari, Kab. Tanah Laut, Provinsi Kalimantan Selatan, Kode Pos: 70815'
    no_telp = setting.no_telp if setting and setting.no_telp else '+62 9512 4024 04'
    email = setting.email if setting and setting.email else 'thesisedukasinusantara@gmail.com'

    return {
        'baseurl': 'http://localhost:8000/',
        'web_setting': setting,
        'web_name': nama_web,
        'webname': 'ThesisEdu',
        'address': alamat,
        'telp': no_telp,
        'email': email,
        'website': 'thesisedu.org',
        'api_qrcode' : 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=',
        'versi' : 'v1.2.0-alpha.1',
        'create_by' : '© 2026 HermantoXYZ.',
    }


# Izin adding versi static kak, (proble browsing chace css)
def versioned_static(request):
    version = 'v1.1.1s.1.X'  # You can update this version number when needed
    return {
        'STATIC_VERSION': version,
    }