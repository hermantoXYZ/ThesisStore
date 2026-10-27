from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from .models import UserAdmin, UserPengguna, Provinsi, Books, CategoryBooks


@login_required
def index(request):
    today = timezone.localdate()
    if request.user.last_name == 'Super Admin':
        userC = UserAdmin.objects.filter(username=request.user).first()
        total_pengguna = UserPengguna.objects.count()
        total_provinsi = Provinsi.objects.count()
        total_buku = Books.objects.count()
        total_kategori = CategoryBooks.objects.count()

        context = {
            'title': 'Dashboard',
            'heading': 'Dashboard Administrator',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC if userC else None,
            'total_pengguna': total_pengguna,
            'total_provinsi': total_provinsi,
            'total_buku': total_buku,
            'total_kategori': total_kategori,
        }
        return render(request, 'admin_super/index.html', context)

    elif request.user.last_name == 'Pengguna':
        userC = UserPengguna.objects.filter(user=request.user).first()

        if not userC:
            messages.error(request, 'Profil pengguna belum tersedia.')
            return redirect('app:profile_pengguna')

        if not userC.photo or not userC.telp or not userC.provinsi_anggota or not userC.alamat:
            messages.error(request, 'Harap lengkapi profil Anda terlebih dahulu.')
            return redirect('app:profile_pengguna')
            
        context = {
            'title': 'Dashboard',
            'heading': 'Dashboard Pengguna',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'today': today,
        }
        return render(request, 'pengguna/index.html', context)
    