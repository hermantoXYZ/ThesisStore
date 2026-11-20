from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from .models import (
    UserAdmin, UserPengguna, Provinsi, Books, CategoryBooks,
    Course, CourseEnrollment, Order
)

@login_required
def index(request):
    today = timezone.localdate()
    if request.user.last_name == 'Super Admin':
        userC = UserAdmin.objects.filter(username=request.user).first()
        total_pengguna = UserPengguna.objects.count()
        total_provinsi = Provinsi.objects.count()
        total_buku = Books.objects.count()
        total_kategori = CategoryBooks.objects.count()
        total_course = Course.objects.count()
        total_enrollment = CourseEnrollment.objects.count()
        active_enrollment = CourseEnrollment.objects.filter(status__in=['active', 'registered']).count()
        recent_enrollments = CourseEnrollment.objects.select_related('user__user', 'course', 'order').order_by('-enrolled_at')[:6]

        context = {
            'title': 'Dashboard',
            'heading': 'Dashboard Administrator',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC if userC else None,
            'total_pengguna': total_pengguna,
            'total_provinsi': total_provinsi,
            'total_buku': total_buku,
            'total_kategori': total_kategori,
            'total_course': total_course,
            'total_enrollment': total_enrollment,
            'active_enrollment': active_enrollment,
            'recent_enrollments': recent_enrollments,
        }
        return render(request, 'admin_super/index.html', context)

    elif request.user.last_name == 'Pengguna':
        userC = UserPengguna.objects.filter(user=request.user).first()

        if not userC:
            messages.error(request, 'Profil pengguna belum tersedia.')
            return redirect('app:profile_pengguna')

        if not userC.photo or not userC.telp or not userC.provinsi_pengguna or not userC.alamat:
            messages.error(request, 'Harap lengkapi profil Anda terlebih dahulu.')
            return redirect('app:profile_pengguna')

        # Sinkronisasi riwayat pesanan course ke CourseEnrollment
        for ord_item in Order.objects.filter(user=request.user, course_items__isnull=False).distinct():
            ord_item.sync_enrollments()

        my_enrollments = CourseEnrollment.objects.filter(user=userC).select_related('course', 'order').order_by('-enrolled_at')
        count_my_courses = my_enrollments.count()
        count_active_courses = my_enrollments.filter(status__in=['active', 'registered']).count()
        count_completed_courses = my_enrollments.filter(status='completed').count()

        context = {
            'title': 'Dashboard',
            'heading': 'Dashboard Pengguna',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'today': today,
            'my_enrollments': my_enrollments[:4],
            'count_my_courses': count_my_courses,
            'count_active_courses': count_active_courses,
            'count_completed_courses': count_completed_courses,
        }
        return render(request, 'pengguna/index.html', context)
    