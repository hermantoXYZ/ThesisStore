from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.models import UserAdmin, Books, CategoryBooks, MediaBooks, Article, Page, Category, KerjaSama, WebSetting, HeroSlide, DokumentasiArticle, DokumentasiPage
from .form_admin import formProfile, CategoryBooksForm, BooksForm, ArticleForm, PageForm, CategoryForm, WebSettingForm, KerjaSamaForm, HeroSlideForm
from app.decorators_admin import admin_required
from django.db.models import Q
from django.utils.text import slugify

def _get_admin_photo(request):
    useradmin = UserAdmin.objects.filter(username=request.user).first()
    return useradmin.photo if useradmin and useradmin.photo else None


@admin_required
def profile_admin(request):
    try:
        useradmin = UserAdmin.objects.get(username=request.user)
    except UserAdmin.DoesNotExist:
        useradmin = UserAdmin(username=request.user)

    if request.method == 'POST':
        form = formProfile(request.POST, request.FILES, instance=useradmin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('app:profile_admin')
        else:
            messages.error(request, 'Gagal memperbarui profil. Periksa isian form.')
    else:
        form = formProfile(instance=useradmin)

    context = {
        'title': 'Profile Admin',
        'heading': 'Edit Profile Admin',
        'useradmin': useradmin,
        'photo': useradmin.photo if getattr(useradmin, 'photo', None) else None,
        'form': form,
    }
    return render(request, 'admin_super/profile_admin.html', context)


# ==========================================
# KATEGORI BUKU
# ==========================================

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