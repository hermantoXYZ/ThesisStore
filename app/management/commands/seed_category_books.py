
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import CategoryBooks


CATEGORY_BOOKS_LIST = [
    {
        "nama_kategori": "Buku Ajar",
        "deskripsi_kategori": "Buku yang disusun secara sistematis untuk mendukung proses pembelajaran dan perkuliahan."
    },
    {
        "nama_kategori": "Buku Referensi",
        "deskripsi_kategori": "Buku ilmiah yang membahas suatu bidang ilmu secara komprehensif berdasarkan hasil kajian dan penelitian."
    },
    {
        "nama_kategori": "Buku Monograf",
        "deskripsi_kategori": "Buku ilmiah yang membahas satu topik khusus secara mendalam berdasarkan hasil penelitian."
    },
    {
        "nama_kategori": "Book Chapter",
        "deskripsi_kategori": "Bagian atau bab dari sebuah buku ilmiah yang ditulis oleh satu atau beberapa penulis."
    },
    {
        "nama_kategori": "Buku Terjemahan",
        "deskripsi_kategori": "Buku yang diterjemahkan dari bahasa asing ke bahasa Indonesia atau sebaliknya."
    },
    {
        "nama_kategori": "Buku Saduran",
        "deskripsi_kategori": "Buku yang disusun melalui proses pengubahan atau penyesuaian dari karya sumber."
    },
    {
        "nama_kategori": "Buku Suntingan",
        "deskripsi_kategori": "Buku ilmiah yang disusun dari berbagai kontribusi penulis dan melalui proses penyuntingan."
    },
    {
        "nama_kategori": "Modul Pembelajaran",
        "deskripsi_kategori": "Bahan pembelajaran yang disusun secara sistematis untuk membantu pencapaian kompetensi tertentu."
    },
    {
        "nama_kategori": "Buku Panduan",
        "deskripsi_kategori": "Buku yang berisi petunjuk, pedoman, atau prosedur dalam melaksanakan kegiatan tertentu."
    },
    {
        "nama_kategori": "Buku Praktikum",
        "deskripsi_kategori": "Buku yang berisi panduan kegiatan praktikum, eksperimen, dan latihan praktik."
    },
    {
        "nama_kategori": "Buku Populer",
        "deskripsi_kategori": "Buku yang menyampaikan pengetahuan atau hasil kajian ilmiah dengan bahasa yang mudah dipahami masyarakat umum."
    },
    {
        "nama_kategori": "Buku Fiksi",
        "deskripsi_kategori": "Buku yang berisi karya imajinatif seperti novel, cerpen, dan kumpulan cerita."
    },
    {
        "nama_kategori": "Buku Nonfiksi",
        "deskripsi_kategori": "Buku yang menyajikan informasi berdasarkan fakta, pengetahuan, pengalaman, atau kejadian nyata."
    },
]


class Command(BaseCommand):
    help = "Menginput data kategori buku"

    def handle(self, *args, **kwargs):
        data = [
            CategoryBooks(
                nama_kategori=item["nama_kategori"],
                slug=slugify(item["nama_kategori"]),
                deskripsi_kategori=item["deskripsi_kategori"]
            )
            for item in CATEGORY_BOOKS_LIST
        ]

        CategoryBooks.objects.bulk_create(
            data,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS("Data kategori buku berhasil diproses.")
        )
