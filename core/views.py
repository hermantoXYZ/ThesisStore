from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import UserAdmin, UserPengguna, Books, CategoryBooks



def loginView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    if request.method == 'POST':
        email = request.POST['email'].strip()
        password = request.POST['password']

        user = User.objects.filter(email=email).first()
        user = authenticate(request, username=user.username, password=password) if user else None

        if user:
            login(request, user)
            messages.success(request, 'Selamat Datang!')
            return redirect('app:dashboard')

        messages.warning(request, 'Email atau password salah.')
        return redirect('login')

    return render(request, 'login.html', {
        'title': 'Login',
        'heading': 'Login',
    })


def registerView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if confirm != password:
            messages.warning(request, 'Password dan konfirmasi password tidak cocok.')
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.warning(request, 'Email sudah terdaftar.')
        else:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                last_name='Pengguna',
            )
            messages.success(request, 'Registrasi berhasil, silakan login.')
            return redirect('login')

    return render(request, 'register.html', {
        'title': 'Daftar Akun',
        'heading': 'Pendaftaran Akun',
    })


@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil logout!')
    return redirect('login')


def homepage(request):
    books = Books.objects.select_related('kategori').prefetch_related('penulis__user', 'media_buku').order_by('-created_at')
    categories = CategoryBooks.objects.filter(aktif=True)
    total_penulis = UserPengguna.objects.count()

    context = {
        'title': 'Beranda',
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'books': books,
        'categories': categories,
        'total_buku': books.count(),
        'total_kategori': categories.count(),
        'total_penulis': total_penulis,
        'jumlah_anggota_institusi': categories.count(),
        'jumlah_anggota_individu': total_penulis,
        'total_ind_inst': total_penulis,
    }
    return render(request, 'homepage/home.html', context)


def buku_detail(request, slug, kategori_slug=None):
    book = get_object_or_404(
        Books.objects.select_related('kategori').prefetch_related('penulis__user', 'editor__user', 'media_buku'),
        slug=slug
    )
    if book.kategori:
        related_books = Books.objects.filter(
            kategori=book.kategori
        ).exclude(pk=book.pk)[:4]
    else:
        related_books = Books.objects.none()
    
    if not related_books.exists():
        related_books = Books.objects.exclude(pk=book.pk).order_by('-created_at')[:4]
    
    # persentase_diskon = int(((book.harga - book.harga_potongan) / book.harga) * 100) if book.harga_potongan else 0

    context = {
        'title': book.judul,
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'book': book,
        'related_books': related_books,
        # 'persentase_diskon': persentase_diskon,
    }
    return render(request, 'homepage/buku_detail.html', context)


# Fallback views for public navigation links in base_public.html
def article_list(request):
    return render(request, 'homepage/article_list.html', {
        'title': 'Berita & Artikel',
        'webname': 'ThesisStore',
        'articles': [],
    })


def article_detail(request, slug):
    return render(request, 'homepage/article_detail.html', {
        'title': 'Detail Artikel',
        'webname': 'ThesisStore',
    })


def aktivitas_list(request):
    return render(request, 'homepage/aktivitas_list.html', {
        'title': 'Agenda & Aktivitas',
        'webname': 'ThesisStore',
        'aktivitas_list': [],
    })


def aktivitas_detail(request, slug):
    return render(request, 'homepage/aktivitas_detail.html', {
        'title': 'Detail Aktivitas',
        'webname': 'ThesisStore',
    })


def contact_page(request):
    return render(request, 'homepage/contact.html', {
        'title': 'Hubungi Kami',
        'webname': 'ThesisStore',
    })


def struktur_organisasi(request):
    return render(request, 'homepage/struktur_organisasi.html', {
        'title': 'Struktur Organisasi',
        'webname': 'ThesisStore',
    })


def page_detail(request, slug):
    return render(request, 'homepage/page_detail.html', {
        'title': slug.replace('-', ' ').title(),
        'webname': 'ThesisStore',
        'slug': slug,
    })


def public_dashboard_sebaran(request):
    return render(request, 'homepage/dashboard_sebaran.html', {
        'title': 'Sebaran Wilayah',
        'webname': 'ThesisStore',
    })


def public_dashboard_anggota(request):
    return render(request, 'homepage/dashboard_anggota.html', {
        'title': 'Direktori Anggota Individu',
        'webname': 'ThesisStore',
    })


def public_dashboard_institusi(request):
    return render(request, 'homepage/dashboard_institusi.html', {
        'title': 'Direktori Institusi',
        'webname': 'ThesisStore',
    })