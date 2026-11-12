from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from app.models import (
    UserAdmin, UserPengguna, Books, CategoryBooks, Course, CourseAgenda,
    Article, Category, KerjaSama, HeroSlide, Page, JurnalMaster, Cart, CartItem
)
from django.urls import reverse


def _transfer_pending_cart(request, user):
    pending = request.session.pop('pending_cart_item', None)
    if not pending:
        return None

    book_uuid = pending.get('book_uuid')
    course_uuid = pending.get('course_uuid')
    quantity = pending.get('quantity', 1)
    buy_now = pending.get('buy_now', False)

    try:
        if course_uuid:
            course = Course.objects.filter(uuid=course_uuid, is_active=True).first()
            if course:
                cart, _ = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)
                cart_item.quantity = 1
                cart_item.save()
                if buy_now:
                    return reverse('app:checkout')
                else:
                    return reverse('app:cart_view')
        elif book_uuid:
            book = Books.objects.filter(uuid=book_uuid).first()
            if book:
                cart, _ = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
                current_qty = 0 if created else cart_item.quantity
                new_qty = current_qty + quantity
                if book.stok is not None and new_qty > book.stok:
                    new_qty = book.stok
                cart_item.quantity = new_qty
                cart_item.save()

                if buy_now:
                    return reverse('app:checkout')
                else:
                    return reverse('app:cart_view')
    except Exception:
        pass

    return None


def loginView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        email = request.POST['email'].strip()
        password = request.POST['password']
        post_next = request.POST.get('next', '').strip()

        user = User.objects.filter(email=email).first()
        user = authenticate(request, username=user.username, password=password) if user else None

        if user:
            login(request, user)
            messages.success(request, f'Selamat Datang kembali, {user.first_name or user.username}!')

            # Pindahkan keranjang tertunda jika ada
            pending_url = _transfer_pending_cart(request, user)
            if pending_url:
                return redirect(pending_url)

            target = post_next or next_url
            if target and target.startswith('/'):
                return redirect(target)
            return redirect('app:dashboard')

        messages.warning(request, 'Email atau password salah.')
        redirect_to = f"{reverse('login')}?next={post_next}" if post_next else 'login'
        return redirect(redirect_to)

    return render(request, 'login.html', {
        'title': 'Login',
        'heading': 'Login',
        'next': next_url,
    })


def registerView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        post_next = request.POST.get('next', '').strip()

        if confirm != password:
            messages.warning(request, 'Password dan konfirmasi password tidak cocok.')
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.warning(request, 'Email sudah terdaftar.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                last_name='Pengguna',
            )
            UserPengguna.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Pendaftaran berhasil! Selamat datang, {name}.')

            # Pindahkan keranjang tertunda jika ada
            pending_url = _transfer_pending_cart(request, user)
            if pending_url:
                return redirect(pending_url)

            target = post_next or next_url
            if target and target.startswith('/'):
                return redirect(target)
            return redirect('app:dashboard')

    return render(request, 'register.html', {
        'title': 'Daftar Akun',
        'heading': 'Pendaftaran Akun',
        'next': next_url,
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
    courses = Course.objects.filter(is_active=True).prefetch_related('coaches__user').order_by('-created_at')
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('urutan', 'created_at')
    articles = Article.objects.filter(status='published').select_related('author', 'category').order_by('-created_at')[:6]
    if not articles.exists():
        articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:6]

    # Mitra & Kerja Sama
    kerjasama_list = KerjaSama.objects.all().order_by('-created_at')

    context = {
        'title': 'Beranda',
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'books': books,
        'categories': categories,
        'courses': courses,
        'hero_slides': hero_slides,
        'articles': articles,
        'kerjasama_list': kerjasama_list,
        'total_courses': courses.count(),
        'total_buku': books.count(),
        'total_kategori': categories.count(),
        'total_penulis': total_penulis,
        'jumlah_anggota_institusi': categories.count(),
        'jumlah_anggota_individu': total_penulis,
        'total_ind_inst': total_penulis,
    }
    return render(request, 'homepage/home.html', context)


def course_detail(request, slug):
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if not course:
        try:
            import uuid as uuid_pkg
            uuid_pkg.UUID(str(slug))
            course = Course.objects.filter(uuid=slug, is_active=True).first()
        except (ValueError, AttributeError):
            course = None

    if not course:
        course = get_object_or_404(Course, slug=slug, is_active=True)

    if str(course.uuid) == slug and course.slug:
        return redirect('course_detail', slug=course.slug, permanent=True)

    agendas = course.agendas.select_related('pengajar__user').order_by('session_number', 'agenda_date')
    related_courses = Course.objects.filter(is_active=True).exclude(pk=course.pk).order_by('-created_at')[:3]

    context = {
        'title': course.name,
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'course': course,
        'agendas': agendas,
        'related_courses': related_courses,
    }
    return render(request, 'homepage/course_detail.html', context)



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


def article_list(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')

    articles = Article.objects.filter(status='published').select_related('author', 'category').order_by('-created_at')
    if not articles.exists():
        articles = Article.objects.select_related('author', 'category').order_by('-created_at')

    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    categories = Category.objects.all().order_by('name')

    return render(request, 'homepage/article_list.html', {
        'title': 'Berita & Artikel',
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'articles': articles,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    })


def article_detail(request, slug):
    article = Article.objects.filter(slug=slug).select_related('author', 'category').first()
    if not article:
        try:
            import uuid as uuid_pkg
            uuid_pkg.UUID(str(slug))
            article = Article.objects.filter(id=slug).select_related('author', 'category').first()
        except (ValueError, AttributeError):
            article = None

    if not article:
        article = get_object_or_404(Article, slug=slug)

    Article.objects.filter(pk=article.pk).update(views_count=(article.views_count or 0) + 1)
    article.refresh_from_db(fields=['views_count'])

    related_articles = Article.objects.filter(status='published').exclude(pk=article.pk)
    if article.category:
        related_articles = related_articles.filter(category=article.category)
    related_articles = related_articles.order_by('-created_at')[:3]

    recent_articles = Article.objects.filter(status='published').exclude(pk=article.pk).order_by('-created_at')[:5]
    categories = Category.objects.all().order_by('name')

    return render(request, 'homepage/article_detail.html', {
        'title': article.title,
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'article': article,
        'related_articles': related_articles,
        'recent_articles': recent_articles,
        'categories': categories,
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
    page = Page.objects.filter(slug=slug).prefetch_related('dokumentasi_foto').first() 
    
    context = {
        'title': page.title,
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'page': page,
        'slug': slug,
    }
    return render(request, 'homepage/page_detail.html', context)


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

def journal_list(request):
    search_query = request.GET.get('q', '').strip()
    journals = JurnalMaster.objects.filter(is_active=True).order_by('nama')

    if search_query:
        journals = journals.filter(
            Q(nama__icontains=search_query) |
            Q(singkatan__icontains=search_query) |
            Q(penerbit__icontains=search_query) |
            Q(issn__icontains=search_query) |
            Q(e_issn__icontains=search_query)
        )

    return render(request, 'homepage/journal_list.html', {
        'title': 'Daftar Jurnal Ilmiah',
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'journals': journals,
        'total_jurnal': journals.count(),
        'search_query': search_query,
    })

def katalog_pelatihan(request):
    search_query = request.GET.get('q', '').strip()
    selected_type = request.GET.get('type', 'all')
    selected_format = request.GET.get('format', 'all')
    selected_fee = request.GET.get('fee', 'all')

    courses = Course.objects.filter(is_active=True).prefetch_related('coaches__user', 'agendas').order_by('-created_at')

    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if selected_type and selected_type != 'all':
        courses = courses.filter(course_type=selected_type)

    if selected_format and selected_format != 'all':
        courses = courses.filter(format=selected_format)

    if selected_fee and selected_fee != 'all':
        courses = courses.filter(fee_type=selected_fee)

    context = {
        'title': 'Katalog Pelatihan & Course',
        'webname': 'ThesisStore',
        'web_name': 'Toko Buku & Publikasi Akademik',
        'courses': courses,
        'total_courses': courses.count(),
        'search_query': search_query,
        'selected_type': selected_type,
        'selected_format': selected_format,
        'selected_fee': selected_fee,
        'course_types': Course.COURSE_TYPE_CHOICES,
        'format_choices': Course.FORMAT_CHOICES,
    }
    return render(request, 'homepage/katalog_pelatihan.html', context)
    
    