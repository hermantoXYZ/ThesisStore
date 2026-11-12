from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .midtrans import sync_order_status_from_midtrans
from app.models import (
    UserAdmin, Books, CategoryBooks, MediaBooks, Article, Page, Category,
    KerjaSama, WebSetting, HeroSlide, DokumentasiArticle, DokumentasiPage,
    Course, CourseAgenda, JurnalMaster, LoaJurnal, NoSuratThesis, KodeSurat,
    Order, OrderItem
)
from .form_admin import (
    formProfile, CategoryBooksForm, BooksForm, ArticleForm, PageForm, CategoryForm,
    WebSettingForm, KerjaSamaForm, HeroSlideForm, CourseForm, CourseAgendaForm,
    JurnalMasterForm, LoaJurnalForm, KodeSuratForm, NoSuratThesisForm
)
from app.decorators_admin import admin_required
from django.db.models import Q
from django.utils.text import slugify
from .views_admin_set import profile_admin
from django.utils import timezone
from datetime import datetime

def _get_admin_photo(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    return useradmin.photo if useradmin and useradmin.photo else None


@admin_required
def kategori_buku_list(request):
    categories = CategoryBooks.objects.all().order_by('nama_kategori')
    context = {
        'title': 'Kategori Buku',
        'heading': 'Daftar Kategori Buku',
        'categories': categories,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/kategori_buku_list.html', context)


@admin_required
def kategori_buku_tambah(request):
    if request.method == 'POST':
        form = CategoryBooksForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori buku berhasil ditambahkan!')
            return redirect('app:kategori_buku_list')
        else:
            messages.error(request, 'Gagal menambahkan kategori. Silakan periksa isian form.')
    else:
        form = CategoryBooksForm()

    context = {
        'title': 'Tambah Kategori Buku',
        'heading': 'Tambah Kategori Buku',
        'form': form,
        'kategori': None,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/kategori_buku_form.html', context)


@admin_required
def kategori_buku_edit(request, uuid):
    kategori = get_object_or_404(CategoryBooks, uuid=uuid)
    if request.method == 'POST':
        form = CategoryBooksForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori buku berhasil diperbarui!')
            return redirect('app:kategori_buku_list')
        else:
            messages.error(request, 'Gagal memperbarui kategori. Silakan periksa isian form.')
    else:
        form = CategoryBooksForm(instance=kategori)

    context = {
        'title': 'Edit Kategori Buku',
        'heading': 'Edit Kategori Buku',
        'form': form,
        'kategori': kategori,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/kategori_buku_form.html', context)


@admin_required
def kategori_buku_hapus(request, uuid):
    kategori = get_object_or_404(CategoryBooks, uuid=uuid)
    nama = kategori.nama_kategori
    kategori.delete()
    messages.success(request, f'Kategori "{nama}" berhasil dihapus!')
    return redirect('app:kategori_buku_list')


# ==========================================
# KELOLA BUKU
# ==========================================

@admin_required
def buku_list(request):
    books = Books.objects.select_related('kategori').prefetch_related('penulis__user', 'editor__user').order_by('-created_at')
    context = {
        'title': 'Kelola Buku',
        'heading': 'Daftar Buku',
        'books': books,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/buku_list.html', context)


@admin_required
def buku_tambah(request):
    if request.method == 'POST':
        form = BooksForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()

            # Simpan multiple media files jika ada
            media_files = request.FILES.getlist('media_files')
            for f in media_files:
                MediaBooks.objects.create(book=book, media=f)

            messages.success(request, f'Buku "{book.judul}" berhasil ditambahkan!')
            return redirect('app:buku_list')
        else:
            messages.error(request, 'Gagal menambahkan buku. Silakan periksa isian form.')
    else:
        form = BooksForm()

    context = {
        'title': 'Tambah Buku Baru',
        'heading': 'Tambah Buku Baru',
        'form': form,
        'book': None,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/buku_form.html', context)


@admin_required
def buku_edit(request, uuid):
    book = get_object_or_404(
        Books.objects.prefetch_related('penulis', 'editor', 'media_buku'),
        uuid=uuid
    )
    if request.method == 'POST':
        form = BooksForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()

            # Simpan multiple media files baru jika ada
            media_files = request.FILES.getlist('media_files')
            for f in media_files:
                MediaBooks.objects.create(book=book, media=f)

            messages.success(request, f'Data buku "{book.judul}" berhasil diperbarui oleh admin')
            return redirect('app:buku_edit', uuid=book.uuid)
        else:
            messages.error(request, 'Gagal memperbarui buku. Silakan periksa isian form.')
    else:
        form = BooksForm(instance=book)

    context = {
        'title': 'Edit Buku',
        'heading': 'Edit Buku',
        'form': form,
        'book': book,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/buku_form.html', context)


@admin_required
def buku_hapus(request, uuid):
    book = get_object_or_404(Books, uuid=uuid)
    judul = book.judul
    book.delete()
    messages.success(request, f'Buku "{judul}" berhasil dihapus!')
    return redirect('app:buku_list')


@admin_required
def buku_media_hapus(request, book_uuid, media_uuid):
    media = get_object_or_404(MediaBooks, id=media_uuid, book__uuid=book_uuid)
    media.delete()
    messages.success(request, 'Foto sampul/media buku berhasil dihapus!')
    return redirect('app:buku_edit', uuid=book_uuid)


@admin_required
def article_list(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    articles_qs = Article.objects.select_related('category', 'author').order_by('-created_at')

    if status_filter in ['draft', 'published', 'archived']:
        articles_qs = articles_qs.filter(status=status_filter)

    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    total_articles = Article.objects.count()
    published_count = Article.objects.filter(status='published').count()
    draft_count = Article.objects.filter(status='draft').count()
    archived_count = Article.objects.filter(status='archived').count()

    context = {
        'title': 'List Berita',
        'heading': 'Daftar Artikel & Berita APBISDI',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'list_articles': articles_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'archived_count': archived_count,
    }
    return render(request, 'admin_super/article_list.html', context)


@admin_required
def article_create(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            if not article.slug:
                article.slug = slugify(article.title)
            article.save()

            files = request.FILES.getlist('dokumentasi_files')
            for f in files:
                DokumentasiArticle.objects.create(article=article, foto=f)

            messages.success(request, f'Artikel "{article.title}" berhasil dibuat!')
            return redirect('app:admin_article_edit', article_id=article.id)
        else:
            messages.error(request, 'Gagal menyimpan artikel. Periksa input form.')
    else:
        form = ArticleForm()

    context = {
        'title': 'Tambah Artikel Baru',
        'heading': 'Tulis Artikel / Berita Baru',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/article_form.html', context)


@admin_required
def article_edit(request, article_id):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            if not updated_article.slug:
                updated_article.slug = slugify(updated_article.title)
            updated_article.save()

            files = request.FILES.getlist('dokumentasi_files')
            for f in files:
                DokumentasiArticle.objects.create(article=updated_article, foto=f)

            messages.success(request, f'Artikel "{updated_article.title}" berhasil diperbarui!')
            return redirect('app:admin_article_edit', article_id=article.id)
        else:
            messages.error(request, 'Gagal memperbarui artikel. Periksa input form.')
    else:
        form = ArticleForm(instance=article)

    context = {
        'title': 'Edit Artikel',
        'heading': f'Edit Artikel: {article.title}',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'article': article,
        'dokumentasi_list': article.dokumentasi_foto.all(),
        'is_edit': True,
    }
    return render(request, 'admin_super/article_form.html', context)


@admin_required
def delete_dokumentasi_article(request, foto_id):
    foto = get_object_or_404(DokumentasiArticle, id=foto_id)
    article_id = foto.article.id
    foto.delete()
    messages.success(request, 'Foto media dokumentasi artikel berhasil dihapus.')
    return redirect('app:admin_article_edit', article_id=article_id)


@admin_required
def article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    title = article.title
    article.delete()
    messages.warning(request, f'Artikel "{title}" berhasil dihapus.')
    return redirect('app:admin_article_list')


@admin_required
def category_list(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            if not category.slug:
                category.slug = slugify(category.name)
            category.save()
            messages.success(request, f'Kategori "{category.name}" berhasil ditambahkan!')
            return redirect('app:admin_category_list')
        else:
            messages.error(request, 'Gagal menambahkan kategori. Pastikan nama belum terdaftar.')
    else:
        form = CategoryForm()

    context = {
        'title': 'Kategori Berita Terkini',
        'heading': 'Kelola Kategori Berita Terkini',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'categories': categories,
        'form': form,
    }
    return render(request, 'admin_super/category_list.html', context)


@admin_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.warning(request, f'Kategori "{name}" berhasil dihapus.')
    return redirect('app:admin_category_list')


@admin_required
def page_list(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    pages = Page.objects.select_related('author').order_by('-created_at')

    context = {
        'title': 'Kelola Halaman',
        'heading': 'Daftar Halaman Statis APBISDI',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'list_pages': pages,
    }
    return render(request, 'admin_super/page_list.html', context)


@admin_required
def page_create(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()

    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user
            if not page.slug:
                page.slug = slugify(page.title)
            page.save()

            files = request.FILES.getlist('dokumentasi_files')
            for f in files:
                DokumentasiPage.objects.create(page=page, foto=f)

            messages.success(request, f'Halaman "{page.title}" berhasil dibuat!')
            return redirect('app:admin_page_list')
        else:
            messages.error(request, 'Gagal menyimpan halaman. Periksa isian form.')
    else:
        form = PageForm()

    context = {
        'title': 'Tambah Halaman Baru',
        'heading': 'Buat Halaman Statis Baru',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/page_form.html', context)


@admin_required
def page_edit(request, page_id):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    page = get_object_or_404(Page, id=page_id)

    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            updated_page = form.save(commit=False)
            if not updated_page.slug:
                updated_page.slug = slugify(updated_page.title)
            updated_page.save()

            # Multiple documentation photos upload
            files = request.FILES.getlist('dokumentasi_files')
            for f in files:
                DokumentasiPage.objects.create(page=updated_page, foto=f)

            messages.success(request, f'Halaman "{updated_page.title}" berhasil diperbarui!')
            return redirect('app:admin_page_list')
        else:
            messages.error(request, 'Gagal memperbarui halaman. Periksa isian form.')
    else:
        form = PageForm(instance=page)

    context = {
        'title': 'Edit Halaman',
        'heading': f'Edit Halaman: {page.title}',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'page': page,
        'dokumentasi_list': page.dokumentasi_foto.all(),
        'is_edit': True,
    }
    return render(request, 'admin_super/page_form.html', context)


@admin_required
def delete_dokumentasi_page(request, foto_id):
    foto = get_object_or_404(DokumentasiPage, id=foto_id)
    page_id = foto.page.id
    foto.delete()
    messages.success(request, 'Foto media dokumentasi halaman berhasil dihapus.')
    return redirect('app:admin_page_edit', page_id=page_id)


@admin_required
def page_delete(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    title = page.title
    page.delete()
    messages.warning(request, f'Halaman "{title}" berhasil dihapus.')
    return redirect('app:admin_page_list')


@admin_required
def web_setting_view(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    setting = WebSetting.objects.first()

    if request.method == 'POST':
        form = WebSettingForm(request.POST, request.FILES, instance=setting) if setting else WebSettingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengaturan website berhasil disimpan!')
            return redirect('app:admin_web_setting')
        else:
            messages.error(request, 'Gagal menyimpan pengaturan. Silakan periksa kembali formulir.')
    else:
        form = WebSettingForm(instance=setting) if setting else WebSettingForm()

    context = {
        'title': 'Pengaturan Website',
        'heading': 'Pengaturan Website & Kontak',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'setting': setting,
    }
    return render(request, 'admin_super/web_setting.html', context)

@admin_required
def kerjasama_list(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    kerjasama_items = KerjaSama.objects.all()

    if request.method == 'POST':
        form = KerjaSamaForm(request.POST, request.FILES)
        if form.is_valid():
            ks = form.save()
            messages.success(request, f'Mitra kerja sama "{ks.nama_kerjasama}" berhasil ditambahkan!')
            return redirect('app:admin_kerjasama_list')
        else:
            messages.error(request, 'Gagal menambahkan mitra kerja sama. Periksa inputan formulir.')
    else:
        form = KerjaSamaForm()

    context = {
        'title': 'Kelola Kerja Sama',
        'heading': 'Kelola Mitra & Kerja Sama',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'kerjasama_list': kerjasama_items,
        'form': form,
    }
    return render(request, 'admin_super/kerjasama_list.html', context)


@admin_required
def kerjasama_edit(request, kerjasama_id):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    ks = get_object_or_404(KerjaSama, id=kerjasama_id)

    if request.method == 'POST':
        form = KerjaSamaForm(request.POST, request.FILES, instance=ks)
        if form.is_valid():
            updated = form.save()
            messages.success(request, f'Mitra kerja sama "{updated.nama_kerjasama}" berhasil diperbarui!')
            return redirect('app:admin_kerjasama_list')
        else:
            messages.error(request, 'Gagal memperbarui data kerja sama.')
    else:
        form = KerjaSamaForm(instance=ks)

    context = {
        'title': 'Edit Kerja Sama',
        'heading': f'Edit Kerja Sama: {ks.nama_kerjasama}',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'kerjasama': ks,
    }
    return render(request, 'admin_super/kerjasama_form.html', context)


@admin_required
def kerjasama_delete(request, kerjasama_id):
    ks = get_object_or_404(KerjaSama, id=kerjasama_id)
    nama = ks.nama_kerjasama
    ks.delete()
    messages.warning(request, f'Mitra kerja sama "{nama}" berhasil dihapus.')
    return redirect('app:admin_kerjasama_list')


# =====================================================================
#                      KELOLA HERO SLIDES (BERANDA)
# =====================================================================

@admin_required
def hero_slide_list(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    slides = HeroSlide.objects.all().order_by('urutan', 'created_at')
    if request.method == 'POST':
        slide_id = request.POST.get('toggle_id')
        if slide_id:
            slide = get_object_or_404(HeroSlide, id=slide_id)
            slide.is_active = not slide.is_active
            slide.save()
            status_label = 'diaktifkan' if slide.is_active else 'dinonaktifkan'
            messages.success(request, f'Slide "{slide.judul}" berhasil {status_label}.')
            return redirect('app:admin_hero_slide_list')

    context = {
        'title': 'Hero Slides',
        'heading': 'Kelola Hero Slide Beranda',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'slides': slides,
    }
    return render(request, 'admin_super/hero_slide_list.html', context)


@admin_required
def hero_slide_create(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()

    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = form.save()
            messages.success(request, f'Hero slide "{slide.judul}" berhasil ditambahkan!')
            return redirect('app:admin_hero_slide_list')
        else:
            messages.error(request, 'Gagal menyimpan hero slide. Periksa isian form.')
    else:
        form = HeroSlideForm()

    context = {
        'title': 'Tambah Hero Slide',
        'heading': 'Tambah Slide Baru untuk Hero Beranda',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/hero_slide_form.html', context)


@admin_required
def hero_slide_edit(request, slide_id):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    slide = get_object_or_404(HeroSlide, id=slide_id)

    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            updated = form.save()
            messages.success(request, f'Hero slide "{updated.judul}" berhasil diperbarui!')
            return redirect('app:admin_hero_slide_list')
        else:
            messages.error(request, 'Gagal memperbarui hero slide. Periksa isian form.')
    else:
        form = HeroSlideForm(instance=slide)

    context = {
        'title': 'Edit Hero Slide',
        'heading': f'Edit Slide: {slide.judul}',
        'useradmin': useradmin,
        'photo': useradmin.photo if useradmin else None,
        'form': form,
        'slide': slide,
        'is_edit': True,
    }
    return render(request, 'admin_super/hero_slide_form.html', context)


@admin_required
def hero_slide_delete(request, slide_id):
    slide = get_object_or_404(HeroSlide, id=slide_id)
    judul = slide.judul
    slide.delete()
    messages.warning(request, f'Hero slide "{judul}" berhasil dihapus.')
    return redirect('app:admin_hero_slide_list')

@admin_required
def course_list(request):
    courses = Course.objects.prefetch_related('coaches__user').order_by('-created_at')
    context = {
        'title': 'Kelola Course',
        'heading': 'Daftar Course & Pelatihan',
        'courses': courses,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/course_list.html', context)


@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.name}" berhasil ditambahkan!')
            return redirect('app:admin_course_edit', uuid=course.uuid)
        else:
            messages.error(request, 'Gagal menyimpan course. Silakan periksa isian form.')
    else:
        form = CourseForm()

    context = {
        'title': 'Tambah Course Baru',
        'heading': 'Tambah Course / Pelatihan Baru',
        'form': form,
        'course': None,
        'photo': _get_admin_photo(request),
        'is_edit': False,
    }
    return render(request, 'admin_super/course_form.html', context)


@admin_required
def course_edit(request, uuid):
    course = get_object_or_404(Course.objects.prefetch_related('coaches', 'agendas'), uuid=uuid)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.name}" berhasil diperbarui!')
            return redirect('app:admin_course_edit', uuid=course.uuid)
        else:
            messages.error(request, 'Gagal memperbarui course. Silakan periksa isian form.')
    else:
        form = CourseForm(instance=course)

    agendas = course.agendas.select_related('pengajar__user').order_by('session_number', 'agenda_date')

    context = {
        'title': 'Edit Course',
        'heading': f'Edit Course: {course.name}',
        'form': form,
        'course': course,
        'agendas': agendas,
        'photo': _get_admin_photo(request),
        'is_edit': True,
    }
    return render(request, 'admin_super/course_form.html', context)


@admin_required
def course_delete(request, uuid):
    course = get_object_or_404(Course, uuid=uuid)
    name = course.name
    course.delete()
    messages.warning(request, f'Course "{name}" berhasil dihapus.')
    return redirect('app:admin_course_list')


@admin_required
def course_agenda_add(request, course_uuid):
    course = get_object_or_404(Course, uuid=course_uuid)
    if request.method == 'POST':
        form = CourseAgendaForm(request.POST)
        if form.is_valid():
            agenda = form.save(commit=False)
            agenda.course = course
            agenda.save()
            messages.success(request, f'Agenda sesi "{agenda.title}" berhasil ditambahkan!')
        else:
            messages.error(request, 'Gagal menambahkan agenda. Periksa isian form.')
    return redirect('app:admin_course_edit', uuid=course_uuid)


@admin_required
def course_agenda_edit(request, agenda_id):
    agenda = get_object_or_404(CourseAgenda, id=agenda_id)
    course_uuid = agenda.course.uuid
    if request.method == 'POST':
        form = CourseAgendaForm(request.POST, instance=agenda)
        if form.is_valid():
            form.save()
            messages.success(request, f'Agenda "{agenda.title}" berhasil diperbarui!')
        else:
            messages.error(request, 'Gagal memperbarui agenda.')
    return redirect('app:admin_course_edit', uuid=course_uuid)


@admin_required
def course_agenda_delete(request, agenda_id):
    agenda = get_object_or_404(CourseAgenda, id=agenda_id)
    course_uuid = agenda.course.uuid
    title = agenda.title
    agenda.delete()
    messages.warning(request, f'Agenda "{title}" berhasil dihapus.')
    return redirect('app:admin_course_edit', uuid=course_uuid)


@admin_required
def jurnal_list(request):
    jurnals = JurnalMaster.objects.all()
    context = {
        'title': 'Master Jurnal',
        'heading': 'Kelola Master Jurnal Ilmiah',
        'jurnal_list': jurnals,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/jurnal_list.html', context)


@admin_required
def jurnal_tambah(request):
    if request.method == 'POST':
        form = JurnalMasterForm(request.POST, request.FILES)
        if form.is_valid():
            jurnal = form.save()
            messages.success(request, f'Jurnal "{jurnal.nama}" berhasil ditambahkan!')
            return redirect('app:admin_jurnal_list')
        else:
            messages.error(request, 'Gagal menambahkan jurnal. Periksa kembali isian form.')
    else:
        form = JurnalMasterForm()

    context = {
        'title': 'Tambah Master Jurnal',
        'heading': 'Tambah Master Jurnal Baru',
        'form': form,
        'jurnal': None,
        'photo': _get_admin_photo(request),
        'is_edit': False,
    }
    return render(request, 'admin_super/jurnal_form.html', context)


@admin_required
def jurnal_edit(request, uuid):
    jurnal = get_object_or_404(JurnalMaster, id=uuid)
    if request.method == 'POST':
        form = JurnalMasterForm(request.POST, request.FILES, instance=jurnal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data Jurnal "{jurnal.nama}" berhasil diperbarui!')
            return redirect('app:admin_jurnal_list')
        else:
            messages.error(request, 'Gagal memperbarui data jurnal. Periksa isian form.')
    else:
        form = JurnalMasterForm(instance=jurnal)

    context = {
        'title': 'Edit Master Jurnal',
        'heading': f'Edit Jurnal: {jurnal.nama}',
        'form': form,
        'jurnal': jurnal,
        'photo': _get_admin_photo(request),
        'is_edit': True,
    }
    return render(request, 'admin_super/jurnal_form.html', context)


@admin_required
def jurnal_hapus(request, uuid):
    jurnal = get_object_or_404(JurnalMaster, id=uuid)
    nama = jurnal.nama
    jurnal.delete()
    messages.warning(request, f'Jurnal "{nama}" berhasil dihapus.')
    return redirect('app:admin_jurnal_list')

@admin_required
def loa_jurnal_list(request):
    status_filter = request.GET.get('status', 'all')
    jurnal_filter = request.GET.get('jurnal', 'all')

    loa_qs = LoaJurnal.objects.select_related('nama_jurnal', 'created_by').order_by('-created_at')

    if status_filter in ['accepted', 'declined']:
        loa_qs = loa_qs.filter(status=status_filter)

    if jurnal_filter != 'all':
        loa_qs = loa_qs.filter(nama_jurnal__id=jurnal_filter)

    jurnals = JurnalMaster.objects.all().order_by('nama')

    context = {
        'title': 'LOA Jurnal',
        'heading': 'Daftar Penerbitan LOA Jurnal',
        'loa_list': loa_qs,
        'jurnals': jurnals,
        'status_filter': status_filter,
        'jurnal_filter': jurnal_filter,
        'total_loa': LoaJurnal.objects.count(),
        'accepted_count': LoaJurnal.objects.filter(status='accepted').count(),
        'declined_count': LoaJurnal.objects.filter(status='declined').count(),
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/loa_list.html', context)


@admin_required
def loa_jurnal_tambah(request):
    if request.method == 'POST':
        form = LoaJurnalForm(request.POST)
        if form.is_valid():
            loa = form.save(commit=False)
            loa.created_by = request.user
            if not loa.no_surat:
                tahun = str(timezone.now().year)
                no_surat_cek = NoSuratThesis.objects.filter(tahun=tahun).order_by('-nomor').first()
                if no_surat_cek and no_surat_cek.nomor:
                    next_nomor = no_surat_cek.nomor + 1
                else:
                    next_nomor = 1

                kodesurat = KodeSurat.objects.get(jenis='Letter Of Acceptance')
                if not kodesurat:
                    kodesurat = KodeSurat.objects.create(
                        jenis='Letter Of Acceptance',
                        kode='LOA'
                    )

                addnosurat = NoSuratThesis.objects.create(
                    nomor=next_nomor,
                    kode=f'{kodesurat.kode}/{loa.nama_jurnal.singkatan}',
                    tahun=tahun,
                    perihal=f'Letter Of Acceptance Jurnal {loa.nama_jurnal.nama}',
                    tujuan=loa.penulis if loa.penulis else 'Yth. Redaksi Jurnal Ilmiah',
                    adminp=request.user
                )

                # Format nomor surat resmi LOA
                if loa.nama_jurnal and loa.nama_jurnal.singkatan:
                    loa.no_surat = f"{addnosurat.nomor}/{kodesurat.kode}-{loa.nama_jurnal.singkatan}/{tahun}"
                else:
                    loa.no_surat = f"{addnosurat.nomor}/{kodesurat.kode}/{tahun}"
            else:
                # Jika nomor surat diisi manual, tetap catat ke buku agenda NoSuratThesis
                tahun = str(loa.periode_tahun or timezone.now().year)
                no_surat_cek = NoSuratThesis.objects.filter(tahun=tahun).order_by('-nomor').first()
                next_nomor = (no_surat_cek.nomor + 1) if (no_surat_cek and no_surat_cek.nomor) else 1

                kodesurat = (
                    KodeSurat.objects.filter(kode__iexact='LOA').first() or
                    KodeSurat.objects.filter(jenis__icontains='Letter Of Acceptance').first()
                )
                kode_val = kodesurat.kode if kodesurat else 'LOA'

                NoSuratThesis.objects.create(
                    nomor=next_nomor,
                    kode=kode_val,
                    tahun=tahun,
                    perihal=f'Letter Of Acceptance Jurnal {loa.nama_jurnal.nama if loa.nama_jurnal else ""}'[:255],
                    tujuan=loa.penulis[:255] if loa.penulis else 'Yth. Redaksi Jurnal Ilmiah',
                    adminp=request.user
                )

            loa.save()
            messages.success(request, f'LOA No. "{loa.no_surat}" untuk naskah "{loa.judul_naskah[:40]}..." berhasil dibuat!')
            return redirect('app:admin_loa_jurnal_list')
        else:
            messages.error(request, 'Gagal menyimpan LOA. Periksa isian form.')
    else:
        # Default tahun berjalan
        current_year = timezone.now().year
        form = LoaJurnalForm(initial={'periode_tahun': current_year})

    context = {
        'title': 'Buat LOA Jurnal',
        'heading': 'Penerbitan LOA Jurnal Baru',
        'form': form,
        'loa': None,
        'photo': _get_admin_photo(request),
        'is_edit': False,
    }
    return render(request, 'admin_super/loa_form.html', context)


@admin_required
def loa_jurnal_edit(request, uuid):
    loa = get_object_or_404(LoaJurnal, id=uuid)
    if request.method == 'POST':
        form = LoaJurnalForm(request.POST, instance=loa)
        if form.is_valid():
            form.save()
            messages.success(request, f'LOA No. "{loa.no_surat}" berhasil diperbarui!')
            return redirect('app:admin_loa_jurnal_list')
        else:
            messages.error(request, 'Gagal memperbarui LOA. Periksa isian form.')
    else:
        form = LoaJurnalForm(instance=loa)

    context = {
        'title': 'Edit LOA Jurnal',
        'heading': f'Edit LOA: {loa.no_surat}',
        'form': form,
        'loa': loa,
        'photo': _get_admin_photo(request),
        'is_edit': True,
    }
    return render(request, 'admin_super/loa_form.html', context)


@admin_required
def loa_jurnal_hapus(request, uuid):
    loa = get_object_or_404(LoaJurnal, id=uuid)
    no_surat = loa.no_surat
    loa.delete()
    messages.warning(request, f'LOA "{no_surat}" berhasil dihapus.')
    return redirect('app:admin_loa_jurnal_list')


@admin_required
def loa_jurnal_detail(request, uuid):
    loa = get_object_or_404(LoaJurnal.objects.select_related('nama_jurnal', 'created_by'), id=uuid)
    context = {
        'title': f'Detail LOA - {loa.no_surat}',
        'heading': f'Preview LOA: {loa.no_surat}',
        'loa': loa,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/loa_detail.html', context)

# =====================================================================
#                      3. NOMOR SURAT KELUAR THESIS
# =====================================================================

@admin_required
def surat_list(request):
    current_year = str(timezone.now().year)
    tahun_filter = request.GET.get('tahun', current_year)
    
    surat_qs = NoSuratThesis.objects.select_related('adminp').order_by('-date_in')
    if tahun_filter != 'all':
        surat_qs = surat_qs.filter(tahun=tahun_filter)

    available_years = NoSuratThesis.objects.values_list('tahun', flat=True).distinct().order_by('-tahun')

    context = {
        'title': 'Nomor Surat Thesis',
        'heading': 'Tata Kelola Nomor Surat Keluar',
        'surat_list': surat_qs,
        'tahun_filter': tahun_filter,
        'available_years': available_years,
        'current_year': current_year,
        'total_surat': NoSuratThesis.objects.count(),
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/surat_list.html', context)


@admin_required
def surat_tambah(request):
    current_year = str(timezone.now().year)

    if request.method == 'POST':
        form = NoSuratThesisForm(request.POST)
        if form.is_valid():
            surat = form.save(commit=False)
            surat.adminp = request.user
            surat.save()
            messages.success(request, f'Nomor surat {surat.nomor}/{surat.kode}/{surat.tahun} berhasil dicatat!')
            return redirect('app:admin_surat_list')
        else:
            messages.error(request, 'Gagal mencatat nomor surat. Periksa isian form.')
    else:
        # Rekomendasi nomor berikutnya otomatis berdasarkan tahun berjalan
        last_surat = NoSuratThesis.objects.filter(tahun=current_year).order_by('-nomor').first()
        next_nomor = (last_surat.nomor + 1) if last_surat and last_surat.nomor else 1
        form = NoSuratThesisForm(initial={
            'tahun': current_year,
            'nomor': next_nomor
        })

    kode_surats = KodeSurat.objects.all().order_by('jenis')

    context = {
        'title': 'Ambil Nomor Surat Baru',
        'heading': 'Catat Nomor Surat Keluar Baru',
        'form': form,
        'kode_surats': kode_surats,
        'surat': None,
        'photo': _get_admin_photo(request),
        'is_edit': False,
    }
    return render(request, 'admin_super/surat_form.html', context)


@admin_required
def surat_edit(request, uuid):
    surat = get_object_or_404(NoSuratThesis, id=uuid)
    if request.method == 'POST':
        form = NoSuratThesisForm(request.POST, instance=surat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data surat nomor {surat.nomor}/{surat.kode}/{surat.tahun} berhasil diperbarui!')
            return redirect('app:admin_surat_list')
        else:
            messages.error(request, 'Gagal memperbarui nomor surat. Periksa isian form.')
    else:
        form = NoSuratThesisForm(instance=surat)

    kode_surats = KodeSurat.objects.all().order_by('jenis')

    context = {
        'title': 'Edit Nomor Surat',
        'heading': f'Edit Nomor Surat: {surat.nomor}/{surat.kode}/{surat.tahun}',
        'form': form,
        'kode_surats': kode_surats,
        'surat': surat,
        'photo': _get_admin_photo(request),
        'is_edit': True,
    }
    return render(request, 'admin_super/surat_form.html', context)


@admin_required
def surat_hapus(request, uuid):
    surat = get_object_or_404(NoSuratThesis, id=uuid)
    info = f"{surat.nomor}/{surat.kode}/{surat.tahun}"
    surat.delete()
    messages.warning(request, f'Nomor surat {info} berhasil dihapus.')
    return redirect('app:admin_surat_list')


# =====================================================================
#                      4. KODE KLASIFIKASI SURAT
# =====================================================================

@admin_required
def kode_surat_list(request):
    if request.method == 'POST':
        form = KodeSuratForm(request.POST)
        if form.is_valid():
            ks = form.save()
            messages.success(request, f'Kode surat "{ks.jenis} ({ks.kode})" berhasil ditambahkan!')
            return redirect('app:admin_kode_surat_list')
        else:
            messages.error(request, 'Gagal menambahkan kode surat.')
    else:
        form = KodeSuratForm()

    kode_list = KodeSurat.objects.all().order_by('jenis')

    context = {
        'title': 'Kode Surat',
        'heading': 'Daftar Kode & Klasifikasi Surat',
        'kode_list': kode_list,
        'form': form,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/kode_surat_list.html', context)


@admin_required
def kode_surat_edit(request, uuid):
    ks = get_object_or_404(KodeSurat, id=uuid)
    if request.method == 'POST':
        form = KodeSuratForm(request.POST, instance=ks)
        if form.is_valid():
            form.save()
            messages.success(request, f'Kode surat "{ks.jenis}" berhasil diperbarui!')
            return redirect('app:admin_kode_surat_list')
        else:
            messages.error(request, 'Gagal memperbarui kode surat.')
    else:
        form = KodeSuratForm(instance=ks)

    context = {
        'title': 'Edit Kode Surat',
        'heading': f'Edit Kode: {ks.jenis}',
        'form': form,
        'ks': ks,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/kode_surat_form.html', context)


@admin_required
def kode_surat_hapus(request, uuid):
    ks = get_object_or_404(KodeSurat, id=uuid)
    jenis = ks.jenis
    ks.delete()
    messages.warning(request, f'Kode surat "{jenis}" berhasil dihapus.')
    return redirect('app:admin_kode_surat_list')


# =========================================================================
# KELOLA PESANAN BUKU / E-COMMERCE (ADMIN)
# =========================================================================

@admin_required
def admin_order_list(request):
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()

    orders_qs = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    if status_filter != 'all' and status_filter in dict(Order.STATUS_CHOICES):
        orders_qs = orders_qs.filter(status=status_filter)

    all_orders = Order.objects.all()
    count_all = all_orders.count()
    count_pending = all_orders.filter(status='pending').count()
    count_paid = all_orders.filter(status='paid').count()
    count_processing = all_orders.filter(status='processing').count()
    count_shipped = all_orders.filter(status='shipped').count()
    count_delivered = all_orders.filter(status='delivered').count()

    context = {
        'title': 'Pesanan Toko Buku',
        'heading': 'Kelola Pesanan & Pengiriman Buku',
        'orders': orders_qs,
        'status_filter': status_filter,
        'count_all': count_all,
        'count_pending': count_pending,
        'count_paid': count_paid,
        'count_processing': count_processing,
        'count_shipped': count_shipped,
        'count_delivered': count_delivered,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/order_list.html', context)


@admin_required
def admin_order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__book'),
        order_number=order_number
    )

    # Sinkronisasi status dengan Midtrans jika ada query ?sync=midtrans atau jika order pending via Midtrans
    sync_req = request.GET.get('sync')
    if sync_req == 'midtrans' or (request.method == 'GET' and order.status == 'pending' and (order.snap_token or order.metode_pembayaran == 'Midtrans')):
        try:
            updated, msg = sync_order_status_from_midtrans(order)
            if updated:
                messages.success(request, f'Status pesanan berhasil disinkronkan dengan Midtrans: {msg}')
                if sync_req == 'midtrans':
                    return redirect('app:admin_order_detail', order_number=order.order_number)
            elif sync_req == 'midtrans':
                messages.info(request, f'Hasil cek status Midtrans: {msg}')
                return redirect('app:admin_order_detail', order_number=order.order_number)
        except Exception as e:
            if sync_req == 'midtrans':
                messages.error(request, f'Gagal memeriksa status ke Midtrans: {str(e)}')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        nomor_resi = request.POST.get('nomor_resi', '').strip()
        kurir = request.POST.get('kurir', '').strip()

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
        if nomor_resi:
            order.nomor_resi = nomor_resi
        if kurir:
            order.kurir = kurir

        order.save()
        messages.success(request, f'Status pesanan #{order.order_number} berhasil diperbarui menjadi "{order.get_status_display()}".')
        return redirect('app:admin_order_detail', order_number=order.order_number)

    context = {
        'title': f'Detail Pesanan #{order.order_number}',
        'heading': f'Kelola Pesanan #{order.order_number}',
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'photo': _get_admin_photo(request),
    }
    return render(request, 'admin_super/order_detail.html', context)

