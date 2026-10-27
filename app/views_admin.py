from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.models import UserAdmin, Books, CategoryBooks, MediaBooks
from .form_admin import formProfile, CategoryBooksForm, BooksForm
from app.decorators_admin import admin_required


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

            messages.success(request, f'Data buku "{book.judul}" berhasil diperbarui!')
            return redirect('app:buku_list')
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
