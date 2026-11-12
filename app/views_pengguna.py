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
from .form_pengguna import formProfile
from .models import UserPengguna, Books, Cart, CartItem, Order, OrderItem
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
        'heading': 'Profil Pengguna APBISDI',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'form': form,
    }
    return render(request, 'pengguna/profil_pengguna.html', context)

@pengguna_required
@check_userpengguna
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book', 'book__kategori').order_by('created_at')
    userpengguna = UserPengguna.objects.filter(user=request.user).first()

    total_price = cart.get_total_price()
    total_items = cart.get_total_items()

    context = {
        'title': 'Keranjang Belanja',
        'heading': 'Keranjang Belanja Anda',
        'cart': cart,
        'items': items,
        'total_price': total_price,
        'total_items': total_items,
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
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    current_qty = 0 if created else cart_item.quantity
    new_qty = current_qty + quantity

    if book.stok is not None and new_qty > book.stok:
        new_qty = book.stok
        messages.warning(request, f'Jumlah disesuaikan dengan sisa stok yang tersedia ({book.stok} eks).')

    cart_item.quantity = new_qty
    cart_item.save()

    if buy_now:
        return redirect('app:checkout')

    messages.success(request, f'Buku "{book.judul}" ({quantity} eks) berhasil ditambahkan ke keranjang belanja!')
    return redirect('app:cart_view')


@pengguna_required
@check_userpengguna
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action') or request.GET.get('action')

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
    title = cart_item.book.judul
    cart_item.delete()
    messages.success(request, f'Buku "{title}" berhasil dihapus dari keranjang.')
    return redirect('app:cart_view')

@pengguna_required
@check_userpengguna
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book').all()
    userpengguna = UserPengguna.objects.filter(user=request.user).first()

    if not items.exists():
        messages.warning(request, 'Keranjang belanja Anda masih kosong. Silakan pilih buku terlebih dahulu.')
        return redirect('app:cart_view')

    total_subtotal = cart.get_total_price()
    ongkir = 0 
    total_tagihan = total_subtotal + ongkir

    if request.method == 'POST':
        nama_penerima = request.POST.get('nama_penerima', '').strip()
        no_hp = request.POST.get('no_hp', '').strip()
        alamat_pengiriman = request.POST.get('alamat_pengiriman', '').strip()
        provinsi = request.POST.get('provinsi', '').strip()
        kota = request.POST.get('kota', '').strip()
        kode_pos = request.POST.get('kode_pos', '').strip()
        catatan = request.POST.get('catatan', '').strip()
        metode_pembayaran = request.POST.get('metode_pembayaran', 'Transfer Bank')

        if not nama_penerima or not no_hp or not alamat_pengiriman:
            messages.error(request, 'Nama penerima, No. Handphone, dan Alamat Lengkap wajib diisi.')
            return redirect('app:checkout')

        with transaction.atomic():
            for item in items:
                if item.book.stok is not None and item.quantity > item.book.stok:
                    messages.error(
                        request,
                        f'Stok buku "{item.book.judul}" tidak mencukupi (sisa: {item.book.stok} eks). '
                        f'Silakan perbarui jumlah di keranjang.'
                    )
                    return redirect('app:cart_view')

            today_str = timezone.now().strftime('%Y%m%d')
            rand_code = uuid.uuid4().hex[:5].upper()
            order_number = f"ORD-{today_str}-{rand_code}"

            order = Order.objects.create(
                order_number=order_number,
                user=request.user,
                status='pending',
                nama_penerima=nama_penerima,
                no_hp=no_hp,
                provinsi=provinsi,
                kota=kota,
                kode_pos=kode_pos,
                alamat_pengiriman=alamat_pengiriman,
                catatan=catatan,
                subtotal=total_subtotal,
                ongkir=ongkir,
                total_harga=total_tagihan,
                metode_pembayaran=metode_pembayaran,
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    judul_buku=item.book.judul,
                    harga_satuan=item.get_price(),
                    quantity=item.quantity,
                    subtotal=item.get_subtotal(),
                )
                # Kurangi stok buku
                if item.book.stok is not None:
                    item.book.stok = max(0, item.book.stok - item.quantity)
                    if item.book.stok == 0:
                        item.book.status = 'Habis'
                    item.book.save()
            items.delete()

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

    orders_qs = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

    if status_filter != 'all' and status_filter in dict(Order.STATUS_CHOICES):
        orders_qs = orders_qs.filter(status=status_filter)

    all_orders = Order.objects.filter(user=request.user)
    count_all = all_orders.count()
    count_pending = all_orders.filter(status='pending').count()
    count_paid = all_orders.filter(status='paid').count()
    count_processing = all_orders.filter(status='processing').count()
    count_shipped = all_orders.filter(status='shipped').count()
    count_delivered = all_orders.filter(status='delivered').count()

    context = {
        'title': 'Pesanan Saya',
        'heading': 'Riwayat & Status Pesanan',
        'orders': orders_qs,
        'status_filter': status_filter,
        'count_all': count_all,
        'count_pending': count_pending,
        'count_paid': count_paid,
        'count_processing': count_processing,
        'count_shipped': count_shipped,
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
        Order.objects.prefetch_related('items__book'),
        order_number=order_number,
        user=request.user
    )

    # Sinkronisasi status langsung ke Midtrans jika order masih berstatus pending
    if order.status == 'pending':
        try:
            is_updated, msg = sync_order_status_from_midtrans(order)
            if is_updated and order.status in ('processing', 'paid'):
                messages.success(request, f'Pembayaran pesanan #{order.order_number} berhasil diverifikasi!')
        except Exception:
            pass

    # Buat atau ambil snap token jika metode pembayaran Midtrans (atau jika ingin bayar otomatis)
    snap_token = order.snap_token
    if order.status == 'pending':
        if not snap_token and order.metode_pembayaran in ('Midtrans', 'Payment Gateway', 'Otomatis'):
            try:
                snap_token = create_snap_transaction(order)
            except Exception:
                snap_token = None

    context = {
        'title': f'Detail Pesanan {order.order_number}',
        'heading': f'Pesanan #{order.order_number}',
        'order': order,
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
        order = get_object_or_404(Order.objects.select_for_update(),order_number=order_number, user=request.user)
        if order.status != 'pending':
            messages.error(request, 'Pesanan tidak dapat dibatalkan karena sudah diproses atau dibayar.')
            return redirect('app:pesanan_detail', order_number=order.order_number)

        for item in order.items.select_related('book'):
            if item.book.stok is not None:
                item.book.stok += item.quantity
                item.book.status = 'Tersedia'
                item.book.save()

        # Ubah status pesanan
        order.status = 'cancelled'
        order.save(update_fields=['status'])

    messages.success(
        request,
        f'Pesanan #{order.order_number} berhasil dibatalkan. Stok buku telah dikembalikan.'
    )

    return redirect('app:pesanan_detail', order_number=order.order_number)
    

@pengguna_required
@check_userpengguna
def upload_bukti_transfer(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if request.method == 'POST' and request.FILES.get('bukti_transfer'):
        order.bukti_transfer = request.FILES['bukti_transfer']
        order.status = 'paid' 
        order.save()
        messages.success(request, f'Bukti transfer untuk pesanan #{order.order_number} berhasil diunggah! Admin akan segera memverifikasi pembayaran Anda.')
    else:
        messages.error(request, 'Gagal mengunggah file bukti transfer. Pastikan file berupa gambar atau dokumen PDF.')

    return redirect('app:pesanan_detail', order_number=order.order_number)


@login_required
def get_order_snap_token(request, order_number):
    """API endpoint AJAX untuk mengambil atau membuat Snap Token Midtrans sebuah pesanan."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    token = order.snap_token
    if not token and order.status == 'pending':
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

    # Sinkronisasi status pesanan berdasarkan Midtrans Transaction Status
    if transaction_status in ('capture', 'settlement'):
        if fraud_status == 'challenge':
            order.status = 'paid'
        else:
            order.status = 'processing'
            order.paid_at = timezone.now()
        order.payment_type = payment_type
        order.transaction_id = transaction_id
        order.save()
    elif transaction_status in ('cancel', 'deny', 'expire'):
        order.status = 'cancelled'
        order.save()
    elif transaction_status == 'pending':
        order.status = 'pending'
        order.payment_type = payment_type
        order.save()

    return JsonResponse({'status': 'OK', 'order_status': order.status})
