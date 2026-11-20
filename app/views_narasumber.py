from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from app.decorators_pengguna import pengguna_required, check_userpengguna
from app.models import CourseAgenda, CourseMaterial, CourseQuiz, CourseQuizQuestion, UserPengguna


@pengguna_required
@check_userpengguna
def narasumber_materi_add(request, agenda_uuid):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    agenda = get_object_or_404(CourseAgenda, uuid=agenda_uuid, pengajar=userpengguna)

    if request.method == 'POST':
        CourseMaterial.objects.create(
            agenda=agenda,
            uploaded_by=userpengguna,
            urutan=int(request.POST.get('urutan') or 1),
            judul=request.POST.get('judul', '').strip(),
            url_materi=request.POST.get('url_materi', '').strip() or None,
            is_visible=request.POST.get('is_visible') == 'on',
        )
        messages.success(request, 'Materi berhasil ditambahkan.')
    return redirect('app:my_narasumber_detail', course_uuid=agenda.course.uuid)


@pengguna_required
@check_userpengguna
def narasumber_materi_edit(request, materi_id):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    materi = get_object_or_404(CourseMaterial, id=materi_id, agenda__pengajar=userpengguna)

    if request.method == 'POST':
        materi.urutan = int(request.POST.get('urutan') or 1)
        materi.judul = request.POST.get('judul', '').strip()
        materi.url_materi = request.POST.get('url_materi', '').strip() or None
        materi.is_visible = request.POST.get('is_visible') == 'on'
        materi.save()
        messages.success(request, 'Materi berhasil diperbarui.')
    return redirect('app:my_narasumber_detail', course_uuid=materi.agenda.course.uuid)


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

        return redirect('app:narasumber_agenda_quiz', agenda_id=agenda.id)

    return render(request, 'pengguna/narasumber_agenda_quiz.html', {
        'agenda': agenda,
        'course': agenda.course,
        'quizzes': agenda.quizzes.all(),
    })