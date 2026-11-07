import io
import os
import urllib.request

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from ..models import LoaJurnal

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader

# ─── Color Palette ───────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0a1628")
PURPLE  = colors.HexColor("#7c3aed")
LIGHT   = colors.HexColor("#f1f5f9")
DARK    = colors.HexColor("#1e293b")
GRAY    = colors.HexColor("#64748b")
GREEN   = colors.HexColor("#15803d")
RED     = colors.HexColor("#dc2626")
WHITE   = colors.white
GOLD    = colors.HexColor("#c9a227")


def _bulan_indo(n):
    BULAN = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
             'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    return BULAN[n]


def _fmt_date(d):
    if not d:
        return '–'
    return f"{d.day} {_bulan_indo(d.month)} {d.year}"


def _qr_image(url: str, size_px: int = 200) -> ImageReader | None:
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


def loa_jurnal_print(request, uuid=None, *args, **kwargs):
    """
    Generate PDF Surat Letter of Acceptance (LOA) Jurnal.
    Menerima parameter 'uuid' dari URL ataupun objek 'loa' secara langsung.
    Menghasilkan dokumen resmi A4 Portrait dengan Font Times New Roman.
    """
    loa_obj = None
    if isinstance(uuid, LoaJurnal):
        loa_obj = uuid
    elif uuid is not None:
        loa_obj = get_object_or_404(LoaJurnal.objects.select_related('nama_jurnal', 'created_by'), id=uuid)
    elif 'loa' in kwargs and isinstance(kwargs['loa'], LoaJurnal):
        loa_obj = kwargs['loa']
    elif 'loa_id' in kwargs:
        loa_obj = get_object_or_404(LoaJurnal.objects.select_related('nama_jurnal', 'created_by'), id=kwargs['loa_id'])
    elif len(args) > 0 and isinstance(args[0], LoaJurnal):
        loa_obj = args[0]
    else:
        for k in ('id', 'pk', 'uuid'):
            if k in kwargs:
                loa_obj = get_object_or_404(LoaJurnal.objects.select_related('nama_jurnal', 'created_by'), id=kwargs[k])
                break

    if not loa_obj:
        return HttpResponse("Data LOA tidak ditemukan.", status=404)

    loa = loa_obj
    response = HttpResponse(content_type="application/pdf")
    safe_id = str(loa.id_naskah).replace('/', '-').replace(' ', '_')
    fname = f"LOA_Jurnal_{safe_id}.pdf"
    response["Content-Disposition"] = f'inline; filename="{fname}"'
    is_accepted = loa.status == 'accepted'

    W, H = A4   # 595.27 x 841.89 pt
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Surat LOA Jurnal – {loa.judul_naskah[:60]}")

    margin_l = 2.5 * cm
    margin_r = 2.5 * cm
    content_w = W - margin_l - margin_r

    # ─── HEADER STRIP ────────────────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(0, H - 90, W, 90, fill=1, stroke=0)

    # Get cover image path (either JurnalMaster cover or fallback to themas-cover.png)
    cover_img_path = None
    if loa.nama_jurnal and loa.nama_jurnal.cover:
        try:
            if os.path.exists(loa.nama_jurnal.cover.path):
                cover_img_path = loa.nama_jurnal.cover.path
        except Exception:
            pass
    
    if not cover_img_path:
        fallback_path = os.path.join(settings.MEDIA_ROOT, 'template_sertifikat', 'themas-cover.png')
        if os.path.exists(fallback_path):
            cover_img_path = fallback_path

    # Logo-ish wordmark
    text_start_x = margin_l
    if cover_img_path:
        c.drawImage(cover_img_path, margin_l, H - 80, width=50, height=70)
        text_start_x = margin_l + 65

    jurnal_nama = loa.nama_jurnal.nama if loa.nama_jurnal else "Jurnal Ilmiah"
    penerbit_nama = (loa.nama_jurnal.penerbit if (loa.nama_jurnal and loa.nama_jurnal.penerbit) else "CV Thesis Edukasi Nusantara")
    issn_val = loa.nama_jurnal.issn if (loa.nama_jurnal and loa.nama_jurnal.issn) else "–"
    e_issn_val = loa.nama_jurnal.e_issn if (loa.nama_jurnal and loa.nama_jurnal.e_issn) else "–"

    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 14)
    c.drawString(text_start_x, H - 42, jurnal_nama)
    c.setFont("Times-Roman", 8)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(text_start_x, H - 57, penerbit_nama)
    c.drawString(text_start_x, H - 68, f"ISSN: {issn_val} | E-ISSN: {e_issn_val}")

    # ─── LETTER TITLE ────────────────────────────────────────────────────────
    y_title = H - 120
    c.setFillColor(DARK)
    c.setFont("Times-Bold", 14)
    c.drawCentredString(W/2, y_title, "LETTER OF ACCEPTANCE / LOA")

    # ─── NUMBER BOX (Centered below title, no background) ───────────────────────────────────
    y_box = y_title - 33
    
    nomor_surat_teks = getattr(loa, 'nomor_surat_formatted', None) or loa.no_surat or "-"
    tgl_terbit = _fmt_date(loa.created_at if hasattr(loa, 'created_at') and loa.created_at else now())

    c.setFillColor(DARK)
    c.setFont("Times-Bold", 10)
    c.drawCentredString(W/2, y_box + 12, f"NOMOR: {nomor_surat_teks}")
    
    c.setFillColor(GRAY)
    c.setFont("Times-Roman", 8.5)
    c.drawCentredString(W/2, y_box, f"Diterbitkan: {tgl_terbit}")

    # Divider
    y_div = y_box - 18
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.5)
    c.line(margin_l, y_div, W - margin_r, y_div)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(margin_l, y_div - 3, W - margin_r, y_div - 3)

    # ─── RECIPIENT & SUBJECT ─────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.setFont("Times-Bold", 9.5)
    c.drawString(margin_l, y_div - 22, "Kepada Yth.")
    c.drawString(margin_l, y_div - 34, loa.penulis)
    c.setFont("Times-Roman", 9.5)
    c.drawString(margin_l, y_div - 46, "di Tempat")
    
    c.drawString(margin_l, y_div - 68, "Perihal : Pemberitahuan Penerimaan Naskah (Letter of Acceptance)")

    # ─── BODY TEXT ───────────────────────────────────────────────────────────
    y_body = y_div - 95

    # Opening paragraph
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        name='body',
        fontName='Times-Roman',
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=DARK,
        spaceAfter=8,
    )
    bold_style = ParagraphStyle(
        name='bold_info',
        fontName='Times-Bold',
        fontSize=10,
        leading=15,
        textColor=DARK,
    )
    label_style = ParagraphStyle(
        name='label',
        fontName='Times-Bold',
        fontSize=9,
        leading=13,
        textColor=GRAY,
    )
    value_style = ParagraphStyle(
        name='value',
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        textColor=DARK,
    )

    tgl_surat = tgl_terbit
    nama_jurnal_display = loa.nama_jurnal.nama if (loa.nama_jurnal and loa.nama_jurnal.nama) else "Jurnal Ilmiah"
    opening = Paragraph(
        f"Yang bertanda tangan di bawah ini, Dewan Redaksi <b>{nama_jurnal_display}</b>, dengan ini menyatakan bahwa "
        f"artikel/naskah ilmiah yang diserahkan kepada redaksi jurnal kami dengan rincian sebagai berikut:",
        body_style
    )
    opening.wrap(content_w, 100)
    opening.drawOn(c, margin_l, y_body - opening.height)
    y_body = y_body - opening.height - 10

    # ─── INFO TABLE (Naskah Details) ─────────────────────────────────────────
    info_items = [
        ["ID Naskah",    loa.id_naskah],
        ["Judul Naskah", loa.judul_naskah],
        ["Penulis",      loa.penulis],
        ["Nama Jurnal",  nama_jurnal_display],
        ["Volume / No.", f"Vol. {loa.volume} / No. {loa.nomor_jurnal}"],
        ["Periode Terbit", f"{loa.periode_bulan} {loa.periode_tahun}"],
        ["Status LOA",   loa.get_status_display().upper()],
    ]

    table_data = []
    for label, val in info_items:
        lbl_p = Paragraph(label, label_style)
        if label == "Status LOA":
            val_color = GREEN if is_accepted else RED
            val_p = Paragraph(f'<font color="{val_color.hexval()}">{val}</font>', bold_style)
        elif label == "Judul Naskah":
            val_p = Paragraph(f"<b>{val}</b>", bold_style)
        else:
            val_p = Paragraph(val, value_style)
        table_data.append([lbl_p, ":", val_p])

    col_widths = [3.5 * cm, 0.5 * cm, content_w - 4 * cm]
    tbl = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), WHITE]),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('GRID',         (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ('ROUNDEDCORNERS', [4]),
    ]))
    tbl_w, tbl_h = tbl.wrap(content_w, 300)
    tbl.drawOn(c, margin_l, y_body - tbl_h)
    y_body = y_body - tbl_h - 14

    # ─── Closing paragraphs ───────────────────────────────────────────────────
    if is_accepted:
        closing_text = (
            f"Artikel tersebut telah melalui proses <b>review blind peer</b> dan dinyatakan <b>DITERIMA (ACCEPTED)</b> "
            f"untuk diterbitkan pada Jurnal <b>{nama_jurnal_display}</b>, Volume {loa.volume}, Nomor {loa.nomor_jurnal}, "
            f"Periode {loa.periode_bulan} {loa.periode_tahun}. "
            f"Penulis diwajibkan untuk melakukan perbaikan sesuai catatan reviewer dan mengirimkan revisi akhir "
            f"sebelum batas waktu yang ditentukan oleh redaksi."
        )
    else:
        closing_text = (
            f"Setelah melalui proses <b>review blind peer</b>, dengan menyesal kami menyampaikan bahwa artikel "
            f"tersebut dinyatakan <b>DITOLAK (DECLINED)</b> untuk diterbitkan pada edisi Volume {loa.volume}, "
            f"Nomor {loa.nomor_jurnal}, Periode {loa.periode_bulan} {loa.periode_tahun}. "
            f"Kami mengucapkan terima kasih atas kepercayaan penulis dalam mengirimkan karya ilmiahnya kepada kami."
        )

    closing = Paragraph(closing_text, body_style)
    closing.wrap(content_w, 200)
    closing.drawOn(c, margin_l, y_body - closing.height)
    y_body = y_body - closing.height - 8

    regards = Paragraph(
        "Demikian surat keterangan ini diterbitkan untuk dapat dipergunakan sebagaimana mestinya.",
        body_style
    )
    regards.wrap(content_w, 60)
    regards.drawOn(c, margin_l, y_body - regards.height)
    y_body = y_body - regards.height - 24

    # ─── SIGNATURE BLOCK ─────────────────────────────────────────────────────
    tgl_cetak = _fmt_date(now())
    c.setFillColor(DARK)
    c.setFont("Times-Roman", 9.5)
    c.drawString(W - margin_r - 175, y_body, f"Kalimantan Selatan, {tgl_cetak}")
    c.setFont("Times-Bold", 9.5)
    c.drawString(W - margin_r - 175, y_body - 14, "Redaksi Jurnal ThesisEdu")
    c.setFont("Times-Roman", 8.5)
    c.drawString(W - margin_r - 175, y_body - 26, "CV Thesis Edukasi Nusantara")

    # Signature image setup
    sig_path = None
    if loa.nama_jurnal and loa.nama_jurnal.ttd_gambar:
        try:
            if os.path.exists(loa.nama_jurnal.ttd_gambar.path):
                sig_path = loa.nama_jurnal.ttd_gambar.path
        except Exception:
            pass

    if not sig_path:
        fallback_sig = os.path.join(settings.MEDIA_ROOT, 'template_sertifikat', 'signature.png')
        if os.path.isfile(fallback_sig):
            sig_path = fallback_sig

    sig_y = y_body - 90
    if sig_path:
        c.drawImage(sig_path, W - margin_r - 175, sig_y + 10, width=85, height=52, mask='auto')

    # ─── FOOTER SECTION: QR CODE FOR VERIFICATION ───────────────────────────
    try:
        from django.urls import reverse
        verify_url = request.build_absolute_uri(reverse('app:admin_loa_jurnal_detail', kwargs={'uuid': loa.id}))
    except Exception:
        verify_url = request.build_absolute_uri(f"/app/admin/loa/{loa.id}/detail")
    
    # QR Code on Bottom Left
    c.setFillColor(GRAY)
    c.setFont("Times-Roman", 7.5)
    c.drawString(margin_l, sig_y + 65, "Verifikasi")

    qr_size = 55
    qr_img = _qr_image(verify_url, 120)
    if qr_img:
        c.drawImage(qr_img, margin_l, sig_y, width=qr_size, height=qr_size)

    # ─── FOOTER SECTION: INDEXING LOGOS ──────────────────────────────────────
    if loa.nama_jurnal:
        index_logos = []
        for f in [loa.nama_jurnal.indeks_1, loa.nama_jurnal.indeks_2, loa.nama_jurnal.indeks_3, loa.nama_jurnal.indeks_4]:
            if f:
                try:
                    if os.path.exists(f.path):
                        index_logos.append(f.path)
                except Exception:
                    pass
                    
        if index_logos:
            logo_x = margin_l + 70
            c.setFillColor(GRAY)
            c.setFont("Times-Roman", 7.5)
            c.drawString(logo_x, sig_y + 65, "Terindeks Di:")
            
            for path in index_logos:
                c.drawImage(path, logo_x, sig_y + 12, width=38, height=18, mask='auto')
                logo_x += 45

    # Signer details (either master jurnal settings or default)
    signer_name = "Andi Hermanto"
    signer_role = "Direktur & Ketua Dewan Redaksi"
    if loa.nama_jurnal:
        if loa.nama_jurnal.ttd_nama:
            signer_name = loa.nama_jurnal.ttd_nama
        if loa.nama_jurnal.ttd_jabatan:
            signer_role = loa.nama_jurnal.ttd_jabatan

    c.setFillColor(DARK)
    c.setFont("Times-Bold", 10)
    c.drawString(W - margin_r - 175, sig_y - 2, signer_name)
    c.setFont("Times-Roman", 8.5)
    c.drawString(W - margin_r - 175, sig_y - 14, signer_role)

    # Digital stamp label
    c.setFillColor(PURPLE)
    c.setFont("Times-Bold", 7.5)
    c.drawString(W - margin_r - 175, sig_y - 25, "Ditandatangani Secara Digital")

    # ─── FOOTER ──────────────────────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 30, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Times-Roman", 7)
    c.drawCentredString(W/2, 18, "ThesisEdu · CV Thesis Edukasi Nusantara · www.thesisedu.org")
    c.drawCentredString(W/2, 9, f"Dokumen digenerate secara otomatis pada {tgl_cetak} · Nomor: {nomor_surat_teks}")

    # ─── Left margin accent bar ───────────────────────────────────────────────
    c.setFillColor(PURPLE)
    c.rect(0, 30, 4, H - 120, fill=1, stroke=0)

    c.showPage()
    c.save()

    buf.seek(0)
    response.write(buf.read())
    return response