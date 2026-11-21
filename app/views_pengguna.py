import uuid
import json
from datetime import date
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from .form_pengguna import formProfile
from .models import UserPengguna, Books, Course, CourseAgenda, Cart, CartItem, Order, OrderBookItem, OrderCourseItem, OrderShipping, CallForReviewer, JurnalMaster, CourseMaterial, CourseSurvey, SurveyQuestion, SurveyResponse, CourseQuiz, CourseQuizAttempt, CourseQuizQuestion, CourseMaterialAttempt
from .midtrans import create_snap_transaction, get_snap_js_url, verify_signature, sync_order_status_from_midtrans
from django.urls import reverse
from app.decorators_pengguna import pengguna_required, check_userpengguna

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
        'heading': 'Profil Pengguna',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'form': form,
    }
    return render(request, 'pengguna/profil_pengguna.html', context)

@pengguna_required
@check_userpengguna
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    # Bersihkan item tidak valid jika ada
    cart.items.filter(book__isnull=True, course__isnull=True).delete()
    cart.items.filter(book__isnull=False, course__isnull=False).delete()

    items = cart.items.select_related('book', 'book__kategori', 'course').order_by('created_at')
    userpengguna = UserPengguna.objects.filter(user=request.user).first()

    total_price = cart.get_total_price()
    total_items = cart.get_total_items()
    has_course = items.filter(course__isnull=False).exists()
    has_book = items.filter(book__isnull=False).exists()

    context = {
        'title': 'Keranjang Belanja',
        'heading': 'Keranjang Belanja Anda',
        'cart': cart,
        'items': items,
        'total_price': total_price, 
        'total_items': total_items,
        'has_course': has_course,
        'has_book': has_book,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/keranjang.html', context)


def cart_add(request, book_uuid):
    book = get_object_or_404(Books, uuid=book_uuid)

    if book.status != 'Tersedia' or (book.stok is not None and book.stok <= 0):
        messages.error(request, f'Maaf, stok untuk buku "{book.judul}" saat ini tidak tersedia.')

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    buy_now = request.POST.get('buy_now') == '1'
    if not request.user.is_authenticated:
        request.session['pending_cart_item'] = {
            'book_uuid': str(book.uuid),
            'quantity': quantity,
            'buy_now': buy_now,
        }
        action_text = "melanjutkan checkout langsung" if buy_now else "menambahkan ke keranjang belanja"
        messages.info(
            request,
            f'Silakan daftar atau login untuk {action_text} buku "{book.judul}". '
            f'Buku pilihan Anda telah disimpan otomatis.'
        )
        target_after_auth = reverse('app:checkout') if buy_now else reverse('app:cart_view')
        return redirect(f"{reverse('register')}?next={target_after_auth}")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'quantity': quantity, 'course': None}
    )

    if not created:
        cart_item.course = None
        new_qty = cart_item.quantity + quantity
        if book.stok is not None and new_qty > book.stok:
            new_qty = book.stok
            messages.warning(request, f'Jumlah disesuaikan dengan sisa stok yang tersedia ({book.stok} eks).')
        cart_item.quantity = new_qty
        cart_item.save()
    else:
        if book.stok is not None and cart_item.quantity > book.stok:
            cart_item.quantity = book.stok
            messages.warning(request, f'Jumlah disesuaikan dengan sisa stok yang tersedia ({book.stok} eks).')
            cart_item.save()

    if buy_now:
        return redirect('app:checkout')

    messages.success(request, f'Buku "{book.judul}" ({quantity} eks) berhasil ditambahkan ke keranjang belanja!')
    return redirect('app:cart_view')


def cart_add_course(request, course_uuid):
    course = get_object_or_404(Course, uuid=course_uuid)

    if not course.is_active:
        messages.error(request, f'Maaf, pelatihan/course "{course.name}" saat ini tidak aktif.')
        return redirect('course_detail', slug=course.slug or str(course.uuid))

    # Cek kuota peserta jika ada batas
    if course.max_participants is not None:
        registered_count = OrderCourseItem.objects.filter(
            course=course,
            order__payment_status__in=['paid', 'not_required']
        ).exclude(order__status='cancelled').count()
        if registered_count >= course.max_participants:
            messages.error(request, f'Maaf, kuota peserta untuk "{course.name}" telah penuh.')
            return redirect('course_detail', slug=course.slug or str(course.uuid))

    # Cek batas pendaftaran jika ada
    if course.registration_deadline and timezone.now() > course.registration_deadline:
        messages.error(request, f'Maaf, batas akhir pendaftaran untuk "{course.name}" telah ditutup.')
        return redirect('course_detail', slug=course.slug or str(course.uuid))

    buy_now = request.POST.get('buy_now') == '1'

    if not request.user.is_authenticated:
        request.session['pending_cart_item'] = {
            'course_uuid': str(course.uuid),
            'quantity': 1,
            'buy_now': buy_now,
        }
        action_text = "mendaftar langsung" if buy_now else "menambahkan ke keranjang"
        messages.info(
            request,
            f'Silakan daftar atau login untuk {action_text} "{course.name}". '
            f'Pilihan pelatihan Anda telah tersimpan otomatis.'
        )
        target_after_auth = reverse('app:checkout') if buy_now else reverse('app:cart_view')
        return redirect(f"{reverse('register')}?next={target_after_auth}")

    # Cek apakah user sudah pernah order/daftar course ini (tidak boleh daftar ulang)
    already_ordered = OrderCourseItem.objects.filter(
        course=course,
        order__user=request.user,
    ).exclude(order__status='cancelled').exclude(order__payment_status='failed').exists()

    if already_ordered:
        messages.warning(request, f'Anda sudah terdaftar di pelatihan "{course.name}". Satu akun hanya dapat mendaftar satu kali.')
        return redirect('course_detail', slug=course.slug or str(course.uuid))

    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Cek apakah course ini sudah ada di keranjang
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        course=course,
        defaults={'quantity': 1, 'book': None}
    )

    if not created:
        messages.info(request, f'Pelatihan "{course.name}" sudah ada di keranjang belanja Anda.')
        return redirect('app:cart_view')

    cart_item.book = None
    cart_item.quantity = 1  # 1 kuota per pendaftaran akun (course tidak boleh > 1)
    cart_item.save()

    if buy_now:
        return redirect('app:checkout')

    messages.success(request, f'Pelatihan "{course.name}" berhasil ditambahkan ke keranjang belanja!')
    return redirect('app:cart_view')


@pengguna_required
@check_userpengguna
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action') or request.GET.get('action')
    item_title = cart_item.course.name if cart_item.course else (cart_item.book.judul if cart_item.book else 'Item')

    if cart_item.course:
        if action in ('decrease', 'remove') or (action == 'set' and str(request.POST.get('quantity')) in ('0', '')):
            cart_item.delete()
            messages.info(request, f'Pelatihan "{item_title}" dihapus dari keranjang.')
        else:
            cart_item.quantity = 1
            cart_item.save()
            messages.info(request, f'Pendaftaran pelatihan dibatasi 1 kuota per akun pengguna.')
        return redirect('app:cart_view')

    if action == 'increase':
        if cart_item.book.stok is None or cart_item.quantity < cart_item.book.stok:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Jumlah "{cart_item.book.judul}" ditambah.')
        else:
            messages.warning(request, f'Stok maksimal untuk buku ini adalah {cart_item.book.stok} eks.')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.info(request, f'Jumlah "{cart_item.book.judul}" dikurangi.')
        else:
            cart_item.delete()
            messages.info(request, f'"{cart_item.book.judul}" dihapus dari keranjang.')
    elif action == 'set':
        try:
            qty = int(request.POST.get('quantity', 1))
            if qty <= 0:
                cart_item.delete()
                messages.info(request, f'"{cart_item.book.judul}" dihapus dari keranjang.')
            else:
                if cart_item.book.stok is not None and qty > cart_item.book.stok:
                    qty = cart_item.book.stok
                    messages.warning(request, f'Jumlah disesuaikan dengan sisa stok ({cart_item.book.stok} eks).')
                cart_item.quantity = qty
                cart_item.save()
        except (ValueError, TypeError):
            pass

    return redirect('app:cart_view')


@pengguna_required
@check_userpengguna
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    title = cart_item.course.name if cart_item.course else (cart_item.book.judul if cart_item.book else 'Item')
    cart_item.delete()
    messages.success(request, f'"{title}" berhasil dihapus dari keranjang.')
    return redirect('app:cart_view')


@pengguna_required
@check_userpengguna
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.filter(book__isnull=True, course__isnull=True).delete()
    cart.items.filter(book__isnull=False, course__isnull=False).delete()

    items = cart.items.select_related('book', 'course').all()
    userpengguna = UserPengguna.objects.filter(user=request.user).first()

    if not items.exists():
        messages.warning(request, 'Keranjang belanja Anda masih kosong. Silakan pilih buku atau pelatihan terlebih dahulu.')
        return redirect('app:cart_view')

    has_physical_book = items.filter(book__isnull=False).exists()
    has_course = items.filter(course__isnull=False).exists()

    for item in items:
        if item.course and item.quantity != 1:
            item.quantity = 1
            item.save(update_fields=['quantity'])

    total_subtotal = cart.get_total_price()
    ongkir = 0 
    total_tagihan = total_subtotal + ongkir

    if request.method == 'POST':
        nama_penerima = request.POST.get('nama_penerima', '').strip()
        no_hp = request.POST.get('no_hp', '').strip()
        alamat_pengiriman = request.POST.get('alamat_pengiriman', '').strip()
        provinsi = request.POST.get('provinsi', '').strip()
        kota = request.POST.get('kota', '').strip()
        kecamatan = request.POST.get('kecamatan', '').strip()
        kelurahan = request.POST.get('kelurahan', '').strip()
        kode_pos = request.POST.get('kode_pos', '').strip()
        catatan = request.POST.get('catatan', '').strip()
        metode_pembayaran = request.POST.get('metode_pembayaran', 'Transfer Bank')

        if has_physical_book:
            if not nama_penerima or not no_hp or not alamat_pengiriman:
                messages.error(request, 'Nama penerima, No. Handphone/WhatsApp, dan Alamat pengiriman wajib diisi.')
                return redirect('app:checkout')
        else:
            if not nama_penerima or not no_hp:
                messages.error(request, 'Nama peserta dan No. Handphone/WhatsApp wajib diisi.')
                return redirect('app:checkout')

        with transaction.atomic():
            for item in items:
                if item.book and item.book.stok is not None and item.quantity > item.book.stok:
                    messages.error(
                        request,
                        f'Stok buku "{item.book.judul}" tidak mencukupi (sisa: {item.book.stok} eks). '
                        f'Silakan perbarui jumlah di keranjang.'
                    )
                    return redirect('app:cart_view')

            today_str = timezone.now().strftime('%Y%m%d')
            rand_code = uuid.uuid4().hex[:5].upper()
            order_number = f"ORD-{today_str}-{rand_code}"

            # Hitung snapshot subtotal dan total transaksi berdasarkan harga checkout saat ini
            computed_subtotal = sum(item.get_subtotal() for item in items)
            computed_total = computed_subtotal + ongkir

            # Status dan payment_status dikelola terpisah
            if computed_total == 0:
                init_status = 'completed'
                init_payment_status = 'not_required'
                metode_pembayaran = 'Gratis'
                paid_at = timezone.now()
            else:
                init_status = 'pending'
                init_payment_status = 'unpaid'
                paid_at = None

            order = Order.objects.create(
                order_number=order_number,
                user=request.user,
                status=init_status,
                payment_status=init_payment_status,
                subtotal=computed_subtotal,
                total_harga=computed_total,
                metode_pembayaran=metode_pembayaran,
                catatan=catatan,
                paid_at=paid_at,
            )

            # OrderShipping hanya dibuat jika transaksi membutuhkan pengiriman fisik (ada buku)
            if has_physical_book:
                OrderShipping.objects.create(
                    order=order,
                    nama_penerima=nama_penerima,
                    no_hp=no_hp,
                    provinsi=provinsi,
                    kota=kota,
                    kecamatan=kecamatan,
                    kelurahan=kelurahan,
                    kode_pos=kode_pos,
                    alamat_pengiriman=alamat_pengiriman,
                    ongkir=ongkir,
                    catatan=catatan,
                )

            # Pisahkan detail buku ke OrderBookItem dan detail course ke OrderCourseItem
            for item in items:
                if item.course:
                    price_snapshot = item.get_price()
                    qty_snapshot = 1  # Course kuantitas maksimal 1
                    subtotal_snapshot = price_snapshot * qty_snapshot
                    OrderCourseItem.objects.create(
                        order=order,
                        course=item.course,
                        nama_produk=item.course.name,
                        harga_satuan=price_snapshot,
                        quantity=qty_snapshot,
                        subtotal=subtotal_snapshot,
                    )
                elif item.book:
                    price_snapshot = item.get_price()
                    qty_snapshot = item.quantity
                    subtotal_snapshot = price_snapshot * qty_snapshot
                    OrderBookItem.objects.create(
                        order=order,
                        book=item.book,
                        nama_produk=item.book.judul,
                        harga_satuan=price_snapshot,
                        quantity=qty_snapshot,
                        subtotal=subtotal_snapshot,
                    )
                    # Kurangi stok buku
                    if item.book.stok is not None:
                        item.book.stok = max(0, item.book.stok - qty_snapshot)
                        if item.book.stok == 0:
                            item.book.status = 'Habis'
                        item.book.save(update_fields=['stok', 'status'])

            items.delete()
            order.sync_enrollments()

            if computed_total == 0:
                messages.success(request, f'Pendaftaran pelatihan #{order.order_number} berhasil! Anda dapat langsung mengakses sesi pelatihan.')
                return redirect('app:pesanan_detail', order_number=order.order_number)

            if metode_pembayaran in ('Midtrans', 'Payment Gateway', 'Otomatis'):
                try:
                    create_snap_transaction(order)
                except Exception:
                    pass

        messages.success(request, f'Pesanan #{order.order_number} berhasil dibuat! Silakan selesaikan pembayaran.')
        return redirect('app:pesanan_detail', order_number=order.order_number)

    default_nama = request.user.get_full_name() or request.user.username
    default_hp = userpengguna.telp if userpengguna else ''
    default_alamat = userpengguna.alamat if userpengguna else ''
    default_provinsi = userpengguna.provinsi_pengguna.nama_provinsi if (userpengguna and userpengguna.provinsi_pengguna) else ''

    context = {
        'title': 'Checkout Pesanan',
        'heading': 'Konfirmasi & Checkout',
        'items': items,
        'cart': cart,
        'has_physical_book': has_physical_book,
        'has_course': has_course,
        'subtotal': total_subtotal,
        'ongkir': ongkir,
        'total_tagihan': total_tagihan,
        'userpengguna': userpengguna,
        'default_nama': default_nama,
        'default_hp': default_hp,
        'default_alamat': default_alamat,
        'default_provinsi': default_provinsi,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/checkout.html', context)

@pengguna_required
@check_userpengguna
def pesanan_list(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    status_filter = request.GET.get('status', 'all')

    orders_qs = Order.objects.filter(user=request.user).prefetch_related(
        'book_items__book', 'course_items__course', 'shipping'
    ).order_by('-created_at')

    if status_filter != 'all':
        if status_filter in dict(Order.ORDER_STATUS_CHOICES):
            orders_qs = orders_qs.filter(status=status_filter)
        elif status_filter in dict(Order.PAYMENT_STATUS_CHOICES):
            orders_qs = orders_qs.filter(payment_status=status_filter)

    all_orders = Order.objects.filter(user=request.user)
    count_all = all_orders.count()
    count_pending = all_orders.filter(status='pending').count()
    count_paid = all_orders.filter(payment_status='paid').count()
    count_processing = all_orders.filter(status='processing').count()
    count_delivered = all_orders.filter(status='completed').count()

    context = {
        'title': 'Pesanan Saya',
        'heading': 'Riwayat & Status Pesanan',
        'orders': orders_qs,
        'status_filter': status_filter,
        'count_all': count_all,
        'count_pending': count_pending,
        'count_paid': count_paid,
        'count_processing': count_processing,
        'count_delivered': count_delivered,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/pesanan_list.html', context)


@pengguna_required
@check_userpengguna
def pesanan_detail(request, order_number):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'book_items__book',
            'course_items__course',
            'course_items__course__agendas'
        ).select_related('shipping'),
        order_number=order_number,
        user=request.user
    )

    if order.status == 'pending':
        try:
            is_updated, msg = sync_order_status_from_midtrans(order)
            if is_updated and (order.payment_status == 'paid' or order.status in ('processing', 'completed')):
                messages.success(request, f'Pembayaran pesanan #{order.order_number} berhasil diverifikasi!')
        except Exception:
            pass

    # Buat atau ambil snap token jika metode pembayaran Midtrans
    snap_token = order.snap_token
    if order.status == 'pending' and order.total_harga > 0 and order.payment_status != 'paid':
        if not snap_token and order.metode_pembayaran in ('Midtrans', 'Payment Gateway', 'Otomatis'):
            try:
                snap_token = create_snap_transaction(order)
            except Exception:
                snap_token = None

    course_items = order.course_items.all()
    has_physical_items = order.book_items.exists()

    context = {
        'title': "Detail Pesanan",
        'heading': f'Pesanan #{order.order_number}',
        'order': order,
        'course_items': course_items,
        'has_course': bool(course_items.exists()),
        'has_physical_items': has_physical_items,
        'snap_token': snap_token,
        'midtrans_client_key': getattr(settings, 'MIDTRANS_CLIENT_KEY', ''),
        'midtrans_snap_js_url': get_snap_js_url(),
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/pesanan_detail.html', context)


@pengguna_required
@check_userpengguna
@require_POST
def batalkan_pesanan(request, order_number):
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), order_number=order_number, user=request.user)
        if order.status != 'pending' or order.payment_status == 'paid':
            messages.error(request, 'Pesanan tidak dapat dibatalkan karena sudah diproses atau dibayar.')
            return redirect('app:pesanan_detail', order_number=order.order_number)

        # Kembalikan stok buku
        for item in order.book_items.select_related('book'):
            if item.book and item.book.stok is not None:
                item.book.stok += item.quantity
                item.book.status = 'Tersedia'
                item.book.save(update_fields=['stok', 'status'])

        order.status = 'cancelled'
        order.save(update_fields=['status'])

    messages.success(
        request,
        f'Pesanan #{order.order_number} berhasil dibatalkan.'
    )

    return redirect('app:pesanan_detail', order_number=order.order_number)


@pengguna_required
@check_userpengguna
def upload_bukti_transfer(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if request.method == 'POST' and request.FILES.get('bukti_transfer'):
        order.bukti_transfer = request.FILES['bukti_transfer']
        order.payment_status = 'pending'  # Menunggu verifikasi admin
        order.save(update_fields=['bukti_transfer', 'payment_status'])
        messages.success(request, f'Bukti transfer untuk pesanan #{order.order_number} berhasil diunggah! Admin akan segera memverifikasi pembayaran Anda.')
    else:
        messages.error(request, 'Gagal mengunggah file bukti transfer. Pastikan file berupa gambar atau dokumen PDF.')

    return redirect('app:pesanan_detail', order_number=order.order_number)


@login_required
def get_order_snap_token(request, order_number):
    """API endpoint AJAX untuk mengambil atau membuat Snap Token Midtrans sebuah pesanan."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    token = order.snap_token
    if not token and order.status == 'pending' and order.payment_status != 'paid':
        token = create_snap_transaction(order)

    return JsonResponse({
        'status': 'success' if token else 'error',
        'snap_token': token,
        'client_key': getattr(settings, 'MIDTRANS_CLIENT_KEY', ''),
        'snap_js_url': get_snap_js_url(),
    })


@login_required
def sync_order_midtrans(request, order_number):
    """API endpoint AJAX untuk mengecek dan menyinkronkan status pesanan langsung dari Midtrans."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    is_updated, message = sync_order_status_from_midtrans(order)
    return JsonResponse({
        'status': 'success',
        'updated': is_updated,
        'order_status': order.status,
        'payment_status': order.payment_status,
        'status_display': order.get_status_display(),
        'message': message,
    })


@csrf_exempt
@require_POST
def midtrans_notification(request):
    """
    Webhook endpoint untuk menerima HTTP Notification / Webhook dari Midtrans.
    Dipanggil otomatis oleh Midtrans saat status pembayaran berubah.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'invalid payload'}, status=400)

    order_id = data.get('order_id')
    status_code = data.get('status_code')
    gross_amount = data.get('gross_amount')
    signature_key = data.get('signature_key')
    transaction_status = data.get('transaction_status')
    fraud_status = data.get('fraud_status')
    payment_type = data.get('payment_type', '')
    transaction_id = data.get('transaction_id', '')

    # Validasi signature Midtrans
    if not verify_signature(order_id, status_code, gross_amount, signature_key):
        return JsonResponse({'status': 'invalid signature'}, status=403)

    order = Order.objects.filter(order_number=order_id).first()
    if not order:
        return JsonResponse({'status': 'order not found'}, status=404)

    # Sinkronisasi status dan payment_status secara terpisah
    if transaction_status in ('capture', 'settlement'):
        if fraud_status == 'challenge':
            order.payment_status = 'pending'
            order.status = 'pending'
        else:
            order.payment_status = 'paid'
            order.status = 'processing'
            if not order.paid_at:
                order.paid_at = timezone.now()
        order.payment_type = payment_type
        order.transaction_id = transaction_id
        order.save(update_fields=['status', 'payment_status', 'paid_at', 'payment_type', 'transaction_id'])
    elif transaction_status in ('cancel', 'deny', 'expire'):
        if transaction_status == 'expire':
            order.payment_status = 'expired'
        else:
            order.payment_status = 'failed'
        order.status = 'cancelled'
        order.save(update_fields=['status', 'payment_status'])
    elif transaction_status == 'pending':
        order.payment_status = 'pending'
        if payment_type and not order.payment_type:
            order.payment_type = payment_type
            order.save(update_fields=['payment_status', 'payment_type'])
        else:
            order.save(update_fields=['payment_status'])

    return JsonResponse({'status': 'OK', 'order_status': order.status, 'payment_status': order.payment_status})


@pengguna_required
@check_userpengguna
def my_courses_list(request):
    """Menampilkan daftar seluruh pelatihan/course yang pernah diikuti/didaftarkan oleh user pengguna."""
    userpengguna = UserPengguna.objects.filter(user=request.user).first()

    status_filter = request.GET.get('status', 'all')
    base_qs = OrderCourseItem.objects.filter(
        order__user=request.user,
        course__isnull=False
    ).select_related('order', 'course').prefetch_related('course__agendas', 'course__coaches__user').order_by('-order__created_at')

    if status_filter == 'active':
        course_items = base_qs.filter(
            Q(order__payment_status__in=['paid', 'not_required']) |
            Q(order__status__in=['processing', 'completed'])
        ).exclude(order__status='cancelled')
    elif status_filter == 'pending':
        course_items = base_qs.filter(
            order__status='pending',
            order__payment_status__in=['unpaid', 'pending']
        )
    elif status_filter in ('delivered', 'completed'):
        course_items = base_qs.filter(order__status='completed')
    else:
        course_items = base_qs

    count_all = base_qs.count()
    count_active = base_qs.filter(
        Q(order__payment_status__in=['paid', 'not_required']) |
        Q(order__status__in=['processing', 'completed'])
    ).exclude(order__status='cancelled').count()
    count_pending = base_qs.filter(
        order__status='pending',
        order__payment_status__in=['unpaid', 'pending']
    ).count()
    count_delivered = base_qs.filter(order__status='completed').count()

    context = {
        'title': 'Pelatihan Saya',
        'heading': 'Pelatihan & Kegiatan Saya',
        'course_items': course_items,
        'status_filter': status_filter,
        'count_all': count_all,
        'count_active': count_active,
        'count_pending': count_pending,
        'count_delivered': count_delivered,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/my_courses_list.html', context)



@pengguna_required
@check_userpengguna
def download_certificate(request, order_item_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    order_item = get_object_or_404(
        OrderCourseItem.objects.select_related('order', 'course').prefetch_related('course__coaches__user'),
        id=order_item_id,
        order__user=request.user,
        course__isnull=False
    )
    course = order_item.course
    order = order_item.order

    is_active = (
        order.payment_status in ('paid', 'not_required') or
        order.status in ('processing', 'completed')
    ) and order.status != 'cancelled'

    if not is_active:
        messages.warning(request, 'Sertifikat baru dapat diakses setelah pembayaran Anda terverifikasi.')
        return redirect('app:my_course_detail', order_item_id=order_item.id)

    cert_number = f"CERT/THESIS/{order.created_at.strftime('%Y%m')}/{str(order_item.id)[:8].upper()}"
    participant_name = (
        userpengguna.nama_lengkap
        if (userpengguna and hasattr(userpengguna, 'nama_lengkap') and userpengguna.nama_lengkap)
        else (request.user.get_full_name() or request.user.username)
    )

    context = {
        'title': f'E-Sertifikat - {course.name}',
        'heading': 'Sertifikat Resmi Pelatihan',
        'order_item': order_item,
        'course': course,
        'order': order,
        'cert_number': cert_number,
        'participant_name': participant_name,
        'userpengguna': userpengguna,
    }
    return render(request, 'pengguna/sertifikat_view.html', context)


@pengguna_required
@check_userpengguna
def apply_journal(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    journals = JurnalMaster.objects.filter(open_registration=True, is_active=True)
    existing_app = CallForReviewer.objects.filter(applicant=userpengguna).first()

    if request.method == 'POST':
        if existing_app and existing_app.status in ('pending', 'approved'):
            messages.warning(request, 'Anda sudah memiliki pendaftaran yang sedang diproses atau telah disetujui.')
            return redirect('app:apply_journal')

        role_applied = request.POST.get('role_applied', 'reviewer')
        journal_ids = request.POST.getlist('journal_interests')

        if not journal_ids:
            messages.error(request, 'Silakan pilih minimal satu jurnal yang diminati.')
            return redirect('app:apply_journal')

        if role_applied not in ('reviewer', 'editor'):
            messages.error(request, 'Peran yang dipilih tidak valid.')
            return redirect('app:apply_journal')

        if existing_app:
            existing_app.role_applied = role_applied
            existing_app.status = 'pending'
            existing_app.verification_notes = ''
            existing_app.save()
            existing_app.journal_interests.set(journals.filter(id__in=journal_ids))
            messages.success(request, 'Pendaftaran Anda telah diperbarui dan sedang menunggu verifikasi admin.')
        else:
            new_app = CallForReviewer.objects.create(
                applicant=userpengguna,
                role_applied=role_applied,
                status='pending',
            )
            new_app.journal_interests.set(journals.filter(id__in=journal_ids))
            messages.success(request, 'Pendaftaran Anda berhasil dikirim! Tim kami akan segera memverifikasi.')

        return redirect('app:apply_journal')
        
    sk_jurnal = None

    if existing_app and existing_app.status == 'approved':
        jurnal = existing_app.journal_interests.first()

        if jurnal and jurnal.file_sk:
            sk_jurnal = jurnal.file_sk.url

    context = {
        'title': 'Review & Editor Journal',
        'heading': 'Daftar sebagai Reviewer / Editor Jurnal',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'journals': journals,
        'existing_app': existing_app,
        'sk_jurnal': sk_jurnal,
    }
    return render(request, 'pengguna/apply_journal.html', context)
@pengguna_required
@check_userpengguna
def my_narasumber_list(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    courses = Course.objects.filter(
        coaches=userpengguna
    ).prefetch_related('agendas', 'coaches__user').order_by('-start_date', '-created_at')

    context = {
        'title': 'Narasumber',
        'heading': 'Kegiatan Sebagai Narasumber',
        'courses': courses,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/my_narasumber_list.html', context)


@pengguna_required
@check_userpengguna
def my_narasumber_detail(request, course_uuid):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'agendas__pengajar__user',
            'agendas__materials',
            'coaches__user',
            'coaches__bidang_keahlian'
        ),
        uuid=course_uuid,
        coaches=userpengguna
    )
    agendas = course.agendas.all().order_by('session_number', 'agenda_date')

    context = {
        'title': f'Detail Narasumber - {course.name}',
        'heading': 'Detail Kegiatan Narasumber',
        'course': course,
        'agendas': agendas,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/my_narasumber_detail.html', context)


@pengguna_required
@check_userpengguna
@require_POST
def narasumber_materi_add(request, agenda_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    # Pastikan user adalah coaches di course DAN pengajar pada agenda ini
    agenda = get_object_or_404(
        CourseAgenda,
        id=agenda_id,
        course__coaches=userpengguna,
        pengajar=userpengguna
    )

    judul = request.POST.get('judul', '').strip()
    url_materi = request.POST.get('url_materi', '').strip()
    is_visible = request.POST.get('is_visible') == 'on'

    if not judul:
        messages.error(request, 'Judul materi wajib diisi.')
        return redirect('app:my_narasumber_detail', course_uuid=agenda.course.uuid)

    CourseMaterial.objects.create(
        agenda=agenda,
        uploaded_by=userpengguna,
        judul=judul,
        url_materi=url_materi or None,
        is_visible=is_visible,
    )
    messages.success(request, f'Materi "{judul}" berhasil ditambahkan ke Sesi #{agenda.session_number or ""}.')
    return redirect('app:my_narasumber_detail', course_uuid=agenda.course.uuid)


@pengguna_required
@check_userpengguna
@require_POST
def narasumber_materi_edit(request, materi_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    # Hanya izinkan edit jika user adalah pengajar pada agenda materi tersebut
    materi = get_object_or_404(
        CourseMaterial,
        id=materi_id,
        agenda__course__coaches=userpengguna,
        agenda__pengajar=userpengguna
    )

    judul = request.POST.get('judul', '').strip()
    url_materi = request.POST.get('url_materi', '').strip()
    is_visible = request.POST.get('is_visible') == 'on'

    if not judul:
        messages.error(request, 'Judul materi wajib diisi.')
        return redirect('app:my_narasumber_detail', course_uuid=materi.agenda.course.uuid)

    materi.judul = judul
    materi.url_materi = url_materi or None
    materi.is_visible = is_visible
    materi.save(update_fields=['judul', 'url_materi', 'is_visible', 'updated_at'])

    messages.success(request, f'Materi "{judul}" berhasil diperbarui.')
    return redirect('app:my_narasumber_detail', course_uuid=materi.agenda.course.uuid)


@pengguna_required
@check_userpengguna
def narasumber_materi_delete(request, materi_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    # Hanya izinkan hapus jika user adalah pengajar pada agenda materi tersebut
    materi = get_object_or_404(
        CourseMaterial,
        id=materi_id,
        agenda__course__coaches=userpengguna,
        agenda__pengajar=userpengguna
    )
    course_uuid = materi.agenda.course.uuid
    judul = materi.judul
    materi.delete()

    messages.success(request, f'Materi "{judul}" berhasil dihapus.')
    return redirect('app:my_narasumber_detail', course_uuid=course_uuid)

@pengguna_required
@check_userpengguna
def my_course_detail(request, order_item_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    order_item = get_object_or_404(
        OrderCourseItem.objects.select_related('order', 'course').prefetch_related(
            'course__agendas__materials',
            'course__agendas__quizzes__questions',
            'course__coaches__user',
            'course__coaches__bidang_keahlian'
        ),
        id=order_item_id,
        order__user=request.user,
        course__isnull=False
    )
    course = order_item.course
    order = order_item.order
    agendas = list(
        course.agendas.all()
        .prefetch_related('materials', 'quizzes__questions')
        .order_by('session_number', 'agenda_date')
    )

    is_active = (
        order.payment_status in ('paid', 'not_required') or
        order.status in ('processing', 'completed')
    ) and order.status != 'cancelled'

    # Ambil semua ID materi yang sudah selesai dibaca oleh user ini (konversi ke str agar pasti cocok)
    completed_materi_ids = [
        str(mid) for mid in CourseMaterialAttempt.objects.filter(
            user=userpengguna,
            is_completed=True,
        ).values_list('material_id', flat=True)
    ] if userpengguna else []

    # Pemetaan riwayat percobaan & nilai tertinggi Pre-Test / Quiz peserta
    attempt_map = {}
    if userpengguna:
        attempts = CourseQuizAttempt.objects.filter(
            user=userpengguna,
            quiz__agenda__course=course,
        )
        for att in attempts:
            qid = att.quiz_id
            if qid not in attempt_map:
                attempt_map[qid] = {
                    'best_score': att.score,
                    'has_passed': att.is_passed,
                }
            else:
                if att.score > attempt_map[qid]['best_score']:
                    attempt_map[qid]['best_score'] = att.score
                if att.is_passed:
                    attempt_map[qid]['has_passed'] = True

    wajib_materi = False
    wajib_quiz = False

    for ag in agendas:
        for m in ag.materials.all():
            m.is_completed = str(m.id) in completed_materi_ids
            if m.is_visible and m.content and not m.is_completed:
                wajib_materi = True

        for qz in ag.quizzes.all():
            info = attempt_map.get(qz.id)
            qz.user_best_score = info['best_score'] if info else None
            qz.user_passed = info['has_passed'] if info else False
            if qz.is_visible and qz.questions.exists() and not qz.user_passed:
                wajib_quiz = True

    wajib_kuesioner = CourseSurvey.objects.filter(
        course=course,
        is_active=True,
        questions__isnull=False
    ).exclude(
        responses__user=userpengguna
    ).exists()

    context = {
        'title': 'Detail Academy',
        'heading': 'Detail Academy',
        'order_item': order_item,
        'course': course,
        'order': order,
        'agendas': agendas,
        'is_active': is_active,
        'wajib_materi': wajib_materi,
        'wajib_quiz': wajib_quiz,
        'wajib_kuesioner': wajib_kuesioner,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'completed_materi_ids': completed_materi_ids,
        'active_sesi': request.GET.get('sesi'),
    }
    return render(request, 'pengguna/my_academy.html', context)

@pengguna_required
@check_userpengguna
def my_course_survey(request, order_item_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    order_item = get_object_or_404(
        OrderCourseItem.objects.select_related('order', 'course'),
        id=order_item_id,
        order__user=request.user,
        course__isnull=False
    )
    course = order_item.course
    order = order_item.order

    is_active = (
        order.payment_status in ('paid', 'not_required') or
        order.status in ('processing', 'completed')
    ) and order.status != 'cancelled'

    if not is_active:
        messages.error(request, 'Selesaikan pembayaran terlebih dahulu sebelum mengisi kuesioner.')
        return redirect('app:my_course_detail', order_item_id=order_item.id)

    survey = get_object_or_404(CourseSurvey, course=course, is_active=True)
    questions = survey.questions.all().order_by('urutan', 'id')
    existing_response = SurveyResponse.objects.filter(survey=survey, user=userpengguna).first()

    if request.method == 'POST':
        if existing_response:
            messages.info(request, 'Anda sudah mengisi kuesioner ini sebelumnya.')
            return redirect('app:my_course_detail', order_item_id=order_item.id)

        answers = {}
        missing_required = False
        for q in questions:
            val = request.POST.get(f'question_{q.id}', '').strip()
            if q.is_required and not val:
                missing_required = True
            answers[str(q.id)] = val

        if missing_required:
            messages.error(request, 'Harap lengkapi semua pertanyaan yang bertanda wajib (*).')
            return redirect('app:my_course_survey', order_item_id=order_item.id)

        SurveyResponse.objects.create(
            survey=survey,
            user=userpengguna,
            answers=answers
        )
        messages.success(request, 'Terima kasih! Kuesioner berhasil dikirim dan E-Sertifikat Anda kini sudah terbuka.')
        return redirect('app:my_course_detail', order_item_id=order_item.id)

    context = {
        'title': f'Kuesioner - {course.name}',
        'heading': 'Kuesioner Evaluasi & Penelitian',
        'order_item': order_item,
        'course': course,
        'survey': survey,
        'questions': questions,
        'existing_response': existing_response,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/my_course_survey.html', context)



@pengguna_required
@check_userpengguna
def my_course_quiz(request, order_item_id, quiz_id):
    userpengguna = get_object_or_404(UserPengguna, user=request.user)
    order_item = get_object_or_404(
        OrderCourseItem,
        id=order_item_id,
        order__user=request.user,
        course__isnull=False,
    )
    course = order_item.course

    quiz = get_object_or_404(
        CourseQuiz.objects.select_related('agenda').prefetch_related('questions'),
        id=quiz_id,
        agenda__course=course,
        is_visible=True,
    )
    questions = quiz.questions.order_by('urutan', 'id')

    if request.method == 'POST':
        total_soal = questions.count()
        benar = 0
        user_answers = {}

        for q in questions:
            jawaban = request.POST.get(f'question_{q.id}', '').strip().upper()
            user_answers[str(q.id)] = jawaban
            if jawaban and jawaban == q.kunci_jawaban:
                benar += 1

        score = round((benar / total_soal) * 100) if total_soal > 0 else 0
        is_passed = score >= quiz.passing_score

        CourseQuizAttempt.objects.create(
            quiz=quiz,
            user=userpengguna,
            answers=user_answers,
            score=score,
            correct_count=benar,
            total_questions=total_soal,
            is_passed=is_passed,
        )

        if is_passed:
            messages.success(
                request,
                f'Selamat! Anda lulus "{quiz.judul}" dengan nilai {score}% ({benar}/{total_soal} benar).'
            )
        else:
            messages.warning(
                request,
                f'Nilai Anda {score}% ({benar}/{total_soal} benar). Minimal lulus adalah {quiz.passing_score}%. Silakan ulangi kembali.'
            )

        return redirect('app:my_course_detail', order_item_id=order_item.id)

    riwayat = CourseQuizAttempt.objects.filter(
        quiz=quiz,
        user=userpengguna,
    ).order_by('-submitted_at')

    return render(request, 'pengguna/my_course_quiz.html', {
        'title': quiz.judul,
        'heading': quiz.get_tipe_tes_display(),
        'order_item': order_item,
        'course': course,
        'quiz': quiz,
        'questions': questions,
        'riwayat': riwayat,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    })

@pengguna_required
@check_userpengguna
def my_course_material_detail(request, order_item_id, materi_id):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    order_item = get_object_or_404(
        OrderCourseItem.objects.select_related('order', 'course'),
        id=order_item_id,
        order__user=request.user,
        course__isnull=False
    )
    course = order_item.course
    order = order_item.order

    is_active = (
        order.payment_status in ('paid', 'not_required') or
        order.status in ('processing', 'completed')
    ) and order.status != 'cancelled'

    if not is_active:
        messages.warning(request, 'Akses materi terbuka setelah pendaftaran Anda diverifikasi.')
        return redirect('app:my_course_detail', order_item_id=order_item.id)

    materi = get_object_or_404(
        CourseMaterial.objects.select_related('agenda', 'uploaded_by__user'),
        id=materi_id,
        agenda__course=course,
        is_visible=True
    )

    if request.method == 'POST' and userpengguna:
        CourseMaterialAttempt.objects.update_or_create(
            material=materi,
            user=userpengguna,
            defaults={'is_completed': True}
        )
        messages.success(request, 'Materi berhasil ditandai selesai dibaca.')
        sesi = materi.agenda.session_number if (materi.agenda and materi.agenda.session_number) else 1
        return redirect(f"{reverse('app:my_course_detail', kwargs={'order_item_id': order_item.id})}?sesi={sesi}")

    is_completed = CourseMaterialAttempt.objects.filter(
        material=materi, user=userpengguna, is_completed=True
    ).exists() if userpengguna else False

    context = {
        'title': materi.judul,
        'heading': 'Detail Materi',
        'order_item': order_item,
        'course': course,
        'order': order,
        'materi': materi,
        'agenda': materi.agenda,
        'is_completed': is_completed,
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
    }
    return render(request, 'pengguna/my_course_material_detail.html', context)