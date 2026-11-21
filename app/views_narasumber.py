from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from app.decorators_pengguna import pengguna_required, check_userpengguna
from app.form_admin import CourseMaterialForm
from app.models import CourseAgenda, CourseMaterial, CourseQuiz, CourseQuizQuestion, UserPengguna


@pengguna_required
@check_userpengguna
def narasumber_agenda_material(request, agenda_uuid):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    agenda = get_object_or_404(
        CourseAgenda.objects.select_related('course', 'pengajar__user'),
        uuid=agenda_uuid,
        pengajar=userpengguna,
    )
    course = agenda.course
    materials = agenda.materials.order_by('urutan', 'id')

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST)
        if form.is_valid():
            materi = form.save(commit=False)
            materi.agenda = agenda
            materi.uploaded_by = userpengguna
            materi.save()
            messages.success(request, f'Materi "{materi.judul}" berhasil ditambahkan.')
            return redirect('app:narasumber_agenda_material', agenda_uuid=agenda.uuid)
        else:
            messages.error(request, 'Gagal menambahkan materi. Periksa kembali isian form.')
    else:
        form = CourseMaterialForm(initial={'urutan': materials.count() + 1, 'is_visible': True})

    return render(request, 'pengguna/narasumber_agenda_material.html', {
        'title': f'Kelola Materi - {agenda.title}',
        'heading': 'Kelola Materi Sesi',
        'course': course,
        'agenda': agenda,
        'materials': materials,
        'form': form,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    })


@pengguna_required
@check_userpengguna
def narasumber_agenda_material_edit(request, materi_id):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    materi = get_object_or_404(
        CourseMaterial.objects.select_related('agenda__course', 'agenda__pengajar__user'),
        id=materi_id,
        agenda__pengajar=userpengguna,
    )
    agenda = materi.agenda
    materials = agenda.materials.order_by('urutan', 'id')

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, instance=materi)
        if form.is_valid():
            form.save()
            messages.success(request, f'Materi "{materi.judul}" berhasil diperbarui.')
            return redirect('app:narasumber_agenda_material', agenda_uuid=agenda.uuid)
        messages.error(request, 'Gagal memperbarui materi. Periksa kembali isian form.')
    else:
        form = CourseMaterialForm(instance=materi)

    return render(request, 'pengguna/narasumber_agenda_material.html', {
        'title': f'Edit Materi - {materi.judul}',
        'heading': 'Edit Materi Sesi',
        'course': agenda.course,
        'agenda': agenda,
        'materials': materials,
        'form': form,
        'edit_materi': materi,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    })


@pengguna_required
@check_userpengguna
def narasumber_materi_add(request, agenda_uuid):
    """Legacy POST-only add — redirect to the full-page form."""
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    agenda = get_object_or_404(CourseAgenda, uuid=agenda_uuid, pengajar=userpengguna)
    return redirect('app:narasumber_agenda_material', agenda_uuid=agenda.uuid)


@pengguna_required
@check_userpengguna
def narasumber_agenda_quiz(request, agenda_uuid):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    agenda = get_object_or_404(
        CourseAgenda.objects.select_related('course').prefetch_related('quizzes__questions'),
        uuid=agenda_uuid,
        pengajar=userpengguna,
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Buat Paket Pre-Test / Quiz Baru
        if action == 'add_quiz':
            CourseQuiz.objects.create(
                agenda=agenda,
                created_by=userpengguna,
                urutan=int(request.POST.get('urutan') or 1),
                tipe_tes=request.POST.get('tipe_tes', 'quiz'),
                judul=request.POST.get('judul', '').strip(),
                passing_score=int(request.POST.get('passing_score') or 70),
                is_visible=request.POST.get('is_visible') == 'on',
            )
            messages.success(request, 'Pre-Test / Quiz berhasil ditambahkan.')

        # 2. Edit Paket Pre-Test / Quiz
        elif action == 'edit_quiz':
            quiz = get_object_or_404(CourseQuiz, id=request.POST.get('quiz_id'), agenda=agenda)
            quiz.urutan = int(request.POST.get('urutan') or 1)
            quiz.tipe_tes = request.POST.get('tipe_tes', 'quiz')
            quiz.judul = request.POST.get('judul', '').strip()
            quiz.passing_score = int(request.POST.get('passing_score') or 70)
            quiz.is_visible = request.POST.get('is_visible') == 'on'
            quiz.save()
            messages.success(request, 'Pengaturan tes berhasil diperbarui.')

        # 3. Hapus Paket Pre-Test / Quiz
        elif action == 'delete_quiz':
            quiz = get_object_or_404(CourseQuiz, id=request.POST.get('quiz_id'), agenda=agenda)
            quiz.delete()
            messages.success(request, 'Pre-Test / Quiz berhasil dihapus.')

        # 4. Tambah Pertanyaan ke Paket Quiz Tertentu
        elif action == 'add_question':
            quiz = get_object_or_404(CourseQuiz, id=request.POST.get('quiz_id'), agenda=agenda)
            CourseQuizQuestion.objects.create(
                quiz=quiz,
                urutan=int(request.POST.get('urutan') or (quiz.questions.count() + 1)),
                pertanyaan=request.POST.get('pertanyaan', '').strip(),
                opsi_a=request.POST.get('opsi_a', '').strip(),
                opsi_b=request.POST.get('opsi_b', '').strip(),
                opsi_c=request.POST.get('opsi_c', '').strip() or None,
                opsi_d=request.POST.get('opsi_d', '').strip() or None,
                kunci_jawaban=request.POST.get('kunci_jawaban', 'A'),
            )
            messages.success(request, 'Pertanyaan berhasil ditambahkan.')

        # 5. Hapus Pertanyaan
        elif action == 'delete_question':
            soal = get_object_or_404(CourseQuizQuestion, id=request.POST.get('question_id'), quiz__agenda=agenda)
            soal.delete()
            messages.success(request, 'Pertanyaan berhasil dihapus.')

        return redirect('app:narasumber_agenda_quiz', agenda_uuid=agenda.uuid)

    return render(request, 'pengguna/narasumber_agenda_quiz.html', {
        'agenda': agenda,
        'course': agenda.course,
        'quizzes': agenda.quizzes.all(),
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    })
