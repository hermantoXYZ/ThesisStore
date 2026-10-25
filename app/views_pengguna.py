from datetime import date
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .form_pengguna import formProfile
from .models import UserPengguna


@login_required
def profile_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = formProfile(request.POST, request.FILES, instance=userpengguna)
        if form.is_valid():
            pengguna = form.save(commit=False)
            pengguna.user = request.user
            pengguna.save()

            messages.success(request, 'Data pengguna berhasil disimpan!')
            return redirect('app:profile_pengguna')

        else:
            messages.error(request, 'Data profil belum lengkap atau terjadi kesalahan pengisian. Silakan periksa kembali.')
    else:
        form = formProfile(instance=userpengguna)

    context = {
        'title': 'Profil Pengguna',
        'heading': 'Profil Pengguna APBISDI',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'form': form,
    }

    return render(request, 'pengguna/profil_pengguna.html', context)
