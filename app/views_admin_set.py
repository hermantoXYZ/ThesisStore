from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import UserAdmin, UserPengguna
from .form_admin import formProfile, UserAccountEditForm, UserPenggunaEditForm, UserAdminEditForm
from app.decorators_admin import admin_required
from django.db.models import Q

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
        'photo': _get_admin_photo(request),
        'form': form,
    }
    return render(request, 'admin_super/profile_admin.html', context)

@admin_required
def user_list(request):
    role = request.GET.get('role', 'Pengguna')
    if role not in ['Pengguna', 'Admin']:
        role = 'Pengguna'

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Password baru dan konfirmasi tidak boleh kosong.")
        elif new_password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok.")
        else:
            target_user = get_object_or_404(User, id=user_id)
            target_user.set_password(new_password)
            target_user.save()
            messages.success(request, f"Password untuk akun {target_user.username} berhasil diganti.")
        return redirect(f"{request.path}?role={role}")

    useradmin = UserAdmin.objects.filter(username=request.user).first()

    if role == 'Admin':
        user_data = UserAdmin.objects.select_related('username').all().order_by('username__date_joined')
    else:
        user_data = UserPengguna.objects.select_related('user', 'bidang_penelitian').all().order_by('-user__date_joined')

    context = {
        'title': f'Daftar {role}',
        'heading': f'Kelola Data Akun {role}',
        'role': role,
        'useradmin': useradmin,
        'photo': _get_admin_photo(request),
        'user_data': user_data,
        'total_pengguna': UserPengguna.objects.count(),
        'total_admin': UserAdmin.objects.count(),
    }
    return render(request, 'admin_super/user_list.html', context)


@admin_required
def user_edit(request, id, role):
    if role not in ['Pengguna', 'Admin']:
        role = 'Pengguna'

    userMaster = get_object_or_404(User, username=id)
    useradmin = UserAdmin.objects.filter(username=request.user).first()

    if role == 'Admin':
        userSelect, _ = UserAdmin.objects.get_or_create(username=userMaster)
        profile_form_class = UserAdminEditForm
    else:
        userSelect, _ = UserPengguna.objects.get_or_create(user=userMaster)
        profile_form_class = UserPenggunaEditForm

    if request.method == 'POST':
        form_account = UserAccountEditForm(request.POST, instance=userMaster)
        form_profile = profile_form_class(request.POST, request.FILES, instance=userSelect)

        if form_account.is_valid() and form_profile.is_valid():
            form_account.save()
            form_profile.save()
            messages.success(request, f'Data {role} "{userMaster.first_name or userMaster.username}" berhasil diperbarui!')
            return redirect('app:user_edit', id=userMaster.username, role=role)
        else:
            messages.error(request, 'Periksa kembali isian formulir. Ada data yang belum sesuai.')
    else:
        form_account = UserAccountEditForm(instance=userMaster)
        form_profile = profile_form_class(instance=userSelect)

    context = {
        'title': f'Edit {role}',
        'heading': f'Edit Data {role}: {userMaster.first_name or userMaster.username}',
        'role': role,
        'useradmin': useradmin,
        'photo': _get_admin_photo(request),
        'usermaster': userMaster,
        'userselect': userSelect,
        'form_account': form_account,
        'form_profile': form_profile,
    }
    return render(request, 'admin_super/user_edit.html', context)
