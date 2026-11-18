
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import BidangIlmu


BIDANG_ILMU_LIST = [
    # Ekonomi
    "Ekonomi Pembangunan",
    "Ekonomi Mikro",
    "Ekonomi Makro",
    "Ekonomi Moneter",
    "Ekonomi Internasional",
    "Ekonomi Publik",
    "Ekonomi Regional",
    "Ekonomi Digital",
    "Ekonomi Islam",
    "Ekonomi Sumber Daya Alam",
    "Ekonomi Ketenagakerjaan",

    # Manajemen
    "Manajemen Keuangan",
    "Manajemen Pemasaran",
    "Manajemen Sumber Daya Manusia",
    "Manajemen Operasional",
    "Manajemen Strategis",
    "Manajemen Risiko",
    "Manajemen Investasi",
    "Manajemen Perbankan",
    "Manajemen Rantai Pasok",
    "Manajemen Inovasi",
    "Manajemen Kewirausahaan",

    # Akuntansi
    "Akuntansi Keuangan",
    "Akuntansi Manajemen",
    "Akuntansi Biaya",
    "Akuntansi Sektor Publik",
    "Akuntansi Perpajakan",
    "Audit dan Assurance",
    "Sistem Informasi Akuntansi",
    "Akuntansi Syariah",
    "Akuntansi Forensik",

    # Bisnis
    "Administrasi Bisnis",
    "Bisnis Internasional",
    "Kewirausahaan",
    "Bisnis dan Perdagangan",
    "Strategi Bisnis",
    "Analisis Bisnis",
    "Bisnis Keluarga",
    "Bisnis Kreatif",

    # Bisnis Digital
    "Digital Marketing",
    "Digital Entrepreneurship",
    "Digital Business Strategy",
    "E-Commerce",
    "Digital Finance",
    "Platform Business",
    "Digital Innovation",
    "Business Intelligence",
    "Digital Transformation",
    "Social Media Marketing",
    "Customer Experience",
    "Digital Business Analytics",

    # Sistem Informasi
    "Sistem Informasi Manajemen",
    "Tata Kelola Teknologi Informasi",
    "Analisis dan Perancangan Sistem",
    "Enterprise Systems",
    "Business Information Systems",
    "Data Management",
    "IT Project Management",
    "Audit Sistem Informasi",
    "E-Government",

    # Teknologi Informasi
    "Jaringan Komputer",
    "Keamanan Informasi",
    "Cloud Computing",
    "Internet of Things",
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
    "Big Data",
    "Software Engineering",
    "Web Development",
    "Mobile Application Development",

    # Ilmu Komputer
    "Algoritma dan Pemrograman",
    "Struktur Data",
    "Basis Data",
    "Kecerdasan Buatan",
    "Komputasi",
    "Computer Vision",
    "Natural Language Processing",
    "Cyber Security",
    "Human Computer Interaction",

    # Pendidikan
    "Pendidikan Ekonomi",
    "Pendidikan Bisnis",
    "Pendidikan Manajemen",
    "Teknologi Pendidikan",
    "Kurikulum dan Pembelajaran",
    "Evaluasi Pendidikan",
    "Pendidikan Vokasi",
    "Pendidikan Digital",
    "Pendidikan Kewirausahaan",

    # Hukum
    "Hukum Perdata",
    "Hukum Pidana",
    "Hukum Tata Negara",
    "Hukum Administrasi Negara",
    "Hukum Bisnis",
    "Hukum Ekonomi",
    "Hukum Internasional",
    "Hukum Kekayaan Intelektual",
    "Hukum Siber",

    # Ilmu Sosial
    "Sosiologi",
    "Ilmu Politik",
    "Antropologi",
    "Hubungan Internasional",
    "Kebijakan Publik",
    "Studi Pembangunan",
    "Sosiologi Ekonomi",
    "Kajian Gender",

    # Teknik
    "Teknik Sipil",
    "Teknik Elektro",
    "Teknik Mesin",
    "Teknik Industri",
    "Teknik Informatika",
    "Teknik Lingkungan",
    "Teknik Kimia",
    "Teknik Komputer",

    # Pertanian
    "Agribisnis",
    "Agroteknologi",
    "Agronomi",
    "Ilmu Tanah",
    "Proteksi Tanaman",
    "Peternakan",
    "Perikanan",
    "Kehutanan",
    "Teknologi Hasil Pertanian",

    # Kesehatan
    "Kedokteran",
    "Kesehatan Masyarakat",
    "Keperawatan",
    "Farmasi",
    "Kebidanan",
    "Gizi",
    "Kesehatan Lingkungan",
    "Administrasi Kesehatan",
    "Epidemiologi",

    # Komunikasi
    "Ilmu Komunikasi",
    "Komunikasi Pemasaran",
    "Public Relations",
    "Jurnalistik",
    "Komunikasi Digital",
    "Media dan Komunikasi",
    "Periklanan",
    "Komunikasi Organisasi",

    # Administrasi Publik
    "Administrasi Negara",
    "Manajemen Publik",
    "Kebijakan Publik",
    "Administrasi Pemerintahan",
    "Pelayanan Publik",
    "Keuangan Negara",
    "Governansi Publik",
    "Manajemen Sektor Publik",

    # Psikologi
    "Psikologi Pendidikan",
    "Psikologi Industri dan Organisasi",
    "Psikologi Sosial",
    "Psikologi Klinis",
    "Psikologi Perkembangan",
    "Psikologi Konsumen",
    "Psikometri",

    # Filsafat
    "Filsafat Ilmu",
    "Filsafat Etika",
    "Filsafat Politik",
    "Filsafat Ekonomi",
    "Logika",
    "Filsafat Pendidikan",

    # Sastra dan Bahasa
    "Sastra Indonesia",
    "Sastra Inggris",
    "Linguistik",
    "Pendidikan Bahasa Indonesia",
    "Pendidikan Bahasa Inggris",
    "Bahasa dan Budaya",
    "Penerjemahan",

    # Sejarah
    "Sejarah Indonesia",
    "Sejarah Dunia",
    "Sejarah Ekonomi",
    "Sejarah Sosial",
    "Arkeologi",
    "Historiografi",
]


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data = [
            BidangIlmu(
                nama=nama,
                slug=slugify(nama),
                aktif=True
            )
            for nama in BIDANG_ILMU_LIST
        ]

        BidangIlmu.objects.bulk_create(
            data,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Data subbidang ilmu berhasil diproses: {len(data)} data."
            )
        )
