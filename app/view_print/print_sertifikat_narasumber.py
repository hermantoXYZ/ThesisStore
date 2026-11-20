import io
import os
import urllib.request
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.models import (
    Course,
    CourseCoachCertificate,
    KodeSurat,
    NoSuratThesis,
    UserPengguna,
)

# Palette warna pendukung
DGRAY  = colors.HexColor("#1a1a2e")
MGRAY  = colors.HexColor("#7a7a8c")
NAVY   = colors.HexColor("#0a1628")
GOLD   = colors.HexColor("#c9a227")
WHITE  = colors.white


def _bulan_indo(n):
    BULAN = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
             'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    return BULAN[n]


def _bulan_romawi(n):
    ROMAWI = ['', 'I', 'II', 'III', 'IV', 'V', 'VI',
              'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    return ROMAWI[n]


def _fmt_date(d):
    if not d:
        return '–'
    return f"{d.day} {_bulan_indo(d.month)} {d.year}"


def _qr_image(url: str, size_px: int = 200):
    api = (
        f"https://api.qrserver.com/v1/create-qr-code/"
        f"?size={size_px}x{size_px}&data={urllib.request.quote(url, safe='')}"
        f"&color=0a1628&bgcolor=ffffff&margin=1"
    )
    try:
        with urllib.request.urlopen(api, timeout=5) as resp:
            return ImageReader(io.BytesIO(resp.read()))
    except Exception:
        return None


def sertifikat_narasumber(request, order_item_id):
    course = Course.objects.prefetch_related(
        'agendas__pengajar__user',
        'agendas__pengajar__bidang_keahlian',
        'coaches__user',
        'coaches__bidang_keahlian',
    ).filter(uuid=order_item_id).first()

    coach_uuid = request.GET.get('coach_uuid')
    if coach_uuid and (request.user.is_staff or request.user.is_superuser):
        dosen = get_object_or_404(UserPengguna, uuid=coach_uuid)
    else:
        dosen = get_object_or_404(UserPengguna, user=request.user)
    is_coach = (
        course.coaches.filter(pk=dosen.pk).exists() or
        course.agendas.filter(pengajar=dosen).exists()
    )
    if not is_coach and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Anda tidak terdaftar sebagai narasumber pada kegiatan ini.')
        return redirect('/')

    # 1. Generate / ambil nomor surat resmi (hanya menyimpan angka urut di CourseCoachCertificate)
    kodesurat = KodeSurat.objects.get(jenis='Pendidikan dan Pelatihan')
    tgl_reg = course.end_date or course.start_date or now()
    tahun = str(tgl_reg.year)
    bulan_romawi = _bulan_romawi(tgl_reg.month)

    coach_cert, created = CourseCoachCertificate.objects.get_or_create(
        course=course,
        coach=dosen,
    )

    if not coach_cert.no_surat:
        nosurat_cek = NoSuratThesis.objects.filter(tahun=tahun).order_by('-nomor').first()
        if nosurat_cek:
            nosurat_baru = nosurat_cek.nomor + 1
        else:
            nosurat_baru = 1

        NoSuratThesis.objects.create(
            adminp=request.user,
            tahun=tahun,
            nomor=nosurat_baru,
            perihal='Sertifikat Narasumber ' + str(course.name),
            tujuan=str(dosen.user.first_name),
            kode=kodesurat.kode,
        )

        coach_cert.no_surat = str(nosurat_baru)
        coach_cert.save()

    cert_number = f"{coach_cert.no_surat}/{kodesurat.kode}/{bulan_romawi}/{tahun}"

    # 2. Siapkan data materi yang diampu narasumber & tanggal pelaksanaan
    agendas_taught = course.agendas.filter(
        Q(pengajar=dosen) | Q(pengajar__isnull=True)
    ).order_by('session_number', 'agenda_date')
    total_jp = agendas_taught.aggregate(total=Sum('jp_count'))['total'] or 0

    if course.start_date and course.end_date and course.start_date != course.end_date:
        tanggal_str = f"{_fmt_date(course.start_date)} s.d. {_fmt_date(course.end_date)}"
    elif course.start_date:
        tanggal_str = _fmt_date(course.start_date)
    else:
        tanggal_str = _fmt_date(course.created_at)

    try:
        verify_path = course.get_absolute_url()
    except Exception:
        verify_path = '/'
    verify_url = request.build_absolute_uri(verify_path)

    nama_dosen = dosen.user.first_name
    instansi_dosen = dosen.universitas or (dosen.bidang_keahlian.nama_bidang if dosen.bidang_keahlian else "Narasumber / Pemateri")

    response = HttpResponse(content_type="application/pdf")
    fname = f"Sertifikat_Narasumber_{course.uuid.hex[:8].upper()}_{dosen.user.username}.pdf"
    response["Content-Disposition"] = f'inline; filename="{fname}"'

    # Dimensi A4 Portrait (595.27 x 841.89)
    W, H = A4
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setTitle(f"Sertifikat Narasumber – {course.name}")

    # 1. DRAW BACKGROUND TEMPLATE IMAGE
    bg_path = os.path.join(settings.MEDIA_ROOT, 'template_sertifikat', 'template_bg_sertifikat.png')
    if os.path.isfile(bg_path):
        p.drawImage(bg_path, 0, 0, width=W, height=H)
    else:
        p.setFillColor(WHITE)
        p.rect(0, 0, W, H, fill=1, stroke=0)
        p.setStrokeColor(GOLD)
        p.setLineWidth(5)
        p.rect(15, 15, W - 30, H - 30, fill=0, stroke=1)

    # 2. TITLE: "Sertifikat"
    p.setFillColor(NAVY)
    p.setFont("Times-BoldItalic", 54)
    p.drawCentredString(W / 2, 620, "Sertifikat")

    # 3. NOMOR SERTIFIKAT
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(W / 2, 585, f"Nomor: {cert_number}")

    # 4. DIBERIKAN KEPADA
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    p.drawCentredString(W / 2, 560, "Diberikan kepada:")

    # 5. NAMA DOSEN / PEMATERI
    p.setFillColor(NAVY)
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(W / 2, 530, nama_dosen)

    # 6. DETAIL EMAIL & INSTANSI
    align_x_lbl = 160
    align_x_val = 265
    p.setFillColor(colors.black)

    p.setFont("Helvetica-Bold", 9)
    p.drawString(align_x_lbl, 502, "Email")
    p.drawString(align_x_val - 15, 502, ":")
    p.setFont("Helvetica", 9)
    p.drawString(align_x_val, 502, str(dosen.user.email or "-"))

    p.setFont("Helvetica-Bold", 9)
    p.drawString(align_x_lbl, 484, "Instansi")
    p.drawString(align_x_val - 15, 484, ":")
    p.setFont("Helvetica", 9)
    p.drawString(align_x_val, 484, str(instansi_dosen))

    # 7. PARAGRAF DESKRIPSI
    desc_html = (
        f"Telah berperan aktif sebagai <b>Narasumber / Pemateri</b> dalam kegiatan <b>{course.get_course_type_display().lower()}</b> "
        f"berjudul <b>\"{course.name}\"</b> yang diselenggarakan oleh <b>ThesisEdu</b> dari "
        f"CV Thesis Edukasi Nusantara secara {course.get_format_display().lower()} pada tanggal <b>{tanggal_str}</b>."
    )
    style_desc = ParagraphStyle(
        name='DescStyle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e293b")
    )
    prg = Paragraph(desc_html, style_desc)
    prg_w = 495
    prg.wrap(prg_w, 100)
    prg.drawOn(p, (W - prg_w) / 2, 420)

    # 8. TABEL STRUKTUR PROGRAM
    style_table_cell = ParagraphStyle(
        name='TableCellStyle',
        fontName='Helvetica',
        fontSize=8,
        leading=9.5,
        textColor=colors.black
    )

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, 398, "Materi yang Disampaikan:")

    y_table = 392
    col_widths = [30, 230, 40, 195]  # No | Materi | JP | Narasumber
    total_w = sum(col_widths)
    margin_x = 50

    # Header Row
    p.setFillColor(colors.HexColor("#f1f5f9"))
    p.setStrokeColor(colors.HexColor("#cbd5e1"))
    p.setLineWidth(0.8)
    p.rect(margin_x, y_table - 20, total_w, 20, fill=1, stroke=1)

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(margin_x + 15, y_table - 13, "No")
    p.drawString(margin_x + 35, y_table - 13, "Materi / Topik Sesi")
    p.drawCentredString(margin_x + 260 + 20, y_table - 13, "JP")
    p.drawString(margin_x + 305, y_table - 13, "Narasumber")

    # Data Rows
    y_row = y_table - 20
    agendas_list = list(agendas_taught)
    bidang = (
        dosen.bidang_keahlian.nama_bidang
        if dosen.bidang_keahlian
        else (dosen.universitas or "Dosen / Pengajar")
    )
    if len(bidang) > 42:
        bidang = bidang[:39] + "..."

    p.setFont("Helvetica", 8)
    if agendas_list:
        for idx, ag in enumerate(agendas_list[:5], 1):
            bg_color = WHITE if idx % 2 != 0 else colors.HexColor("#f8fafc")
            p.setFillColor(bg_color)
            p.rect(margin_x, y_row - 26, total_w, 26, fill=1, stroke=1)

            p.setFillColor(colors.black)
            p.setFont("Helvetica", 8)
            p.drawCentredString(margin_x + 15, y_row - 16, str(idx))

            # Materi Title Wrapping via Paragraph
            materi_prg = Paragraph(ag.title, style_table_cell)
            _, cell_h = materi_prg.wrap(215, 26)
            materi_prg.drawOn(p, margin_x + 35, y_row - 13 - cell_h / 2)

            # JP
            jp_val = f"{ag.jp_count} JP" if ag.jp_count else "–"
            p.drawCentredString(margin_x + 260 + 20, y_row - 16, jp_val)

            # Narasumber Name & Bidang Keahlian
            p.setFont("Helvetica-Bold", 7.5)
            p.drawString(margin_x + 305, y_row - 11, nama_dosen)
            p.setFont("Helvetica-Oblique", 6.5)
            p.drawString(margin_x + 305, y_row - 20, bidang)

            y_row -= 26
    else:
        p.setFillColor(WHITE)
        p.rect(margin_x, y_row - 26, total_w, 26, fill=1, stroke=1)
        p.setFillColor(colors.black)
        p.drawCentredString(margin_x + 15, y_row - 16, "1")

        materi_prg = Paragraph(course.name, style_table_cell)
        _, cell_h = materi_prg.wrap(215, 26)
        materi_prg.drawOn(p, margin_x + 35, y_row - 13 - cell_h / 2)

        p.drawCentredString(margin_x + 260 + 20, y_row - 16, "–")
        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(margin_x + 305, y_row - 11, nama_dosen)
        p.setFont("Helvetica-Oblique", 6.5)
        p.drawString(margin_x + 305, y_row - 20, bidang)
        y_row -= 26

    # Total JP Row
    p.setFillColor(WHITE)
    p.rect(margin_x, y_row - 20, total_w, 20, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 8)
    p.drawString(margin_x + 35, y_row - 14, "Total JP")
    p.drawCentredString(margin_x + 260 + 20, y_row - 14, f"{total_jp} JP" if total_jp else "–")
    y_row -= 20

    # 9. FOOTER SECTION: QR CODE & SIGNATURE
    p.setFillColor(MGRAY)
    p.setFont("Helvetica", 7.5)
    p.drawString(50, 160, "Scan untuk Verifikasi Keaslian Sertifikat")

    qr_size = 72
    qr_img = _qr_image(verify_url, 150)
    if qr_img:
        p.drawImage(qr_img, 50, 80, width=qr_size, height=qr_size)

    p.setFillColor(colors.HexColor("#475569"))
    p.setFont("Helvetica", 7)
    p.drawString(50, 68, "CV. Thesis Edukasi Nusantara")
    p.drawString(50, 59, "SK menteri Hukum dan HAM nomor")
    p.drawString(50, 50, "AHU-0107786-AH.01.14 Tahun 2025")

    # Signature on Bottom Right
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 8.5)
    tgl_cetak = _fmt_date(now())
    p.drawString(380, 150, f"Jombang, {tgl_cetak}")
    p.drawString(380, 138, "Direktur CV Thesis Edukasi Nusantara")

    sig_path = os.path.join(settings.MEDIA_ROOT, 'template_sertifikat', 'signature.png')
    if os.path.isfile(sig_path):
        p.drawImage(sig_path, 370, 90, width=90, height=55, mask='auto')

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(380, 80, "Arpiah")

    p.setFillColor(colors.HexColor("#7c3aed"))
    p.setFont("Helvetica-Bold", 8)
    p.drawString(380, 68, "Ditandatangani Secara Digital")

    # Save
    p.showPage()
    p.save()

    buf.seek(0)
    response.write(buf.read())
    return response