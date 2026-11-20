import base64
import json
import logging
import hashlib
import urllib.request
import urllib.error
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_snap_url():
    if getattr(settings, 'MIDTRANS_IS_PRODUCTION', False):
        return 'https://app.midtrans.com/snap/v1/transactions'
    return 'https://app.sandbox.midtrans.com/snap/v1/transactions'


def get_snap_js_url():
    if getattr(settings, 'MIDTRANS_IS_PRODUCTION', False):
        return 'https://app.midtrans.com/snap/snap.js'
    return 'https://app.sandbox.midtrans.com/snap/snap.js'


def create_snap_transaction(order):
    server_key = getattr(settings, 'MIDTRANS_SERVER_KEY', '')
    if not server_key or 'YOUR_SERVER_KEY' in server_key:
        logger.warning("MIDTRANS_SERVER_KEY belum diisi di settings.")
        return None

    if order.snap_token:
        return order.snap_token

    item_details = []
    for item in order.book_items.select_related('book'):
        item_details.append({
            'id': str(item.book.id if item.book else item.id)[:45],
            'price': int(item.harga_satuan),
            'quantity': int(item.quantity),
            'name': (item.nama_produk or 'Buku')[:50]
        })

    for item in order.course_items.select_related('course'):
        item_details.append({
            'id': str(item.course.uuid if item.course else item.id)[:45],
            'price': int(item.harga_satuan),
            'quantity': int(item.quantity),
            'name': (item.nama_produk or 'Pelatihan')[:50]
        })

    shipping = getattr(order, 'shipping', None)
    if shipping and shipping.ongkir and shipping.ongkir > 0:
        item_details.append({
            'id': 'ONGKIR',
            'price': int(shipping.ongkir),
            'quantity': 1,
            'name': 'Ongkos Kirim'
        })

    gross_amount = int(order.total_harga)

    email = order.user.email if (order.user and order.user.email) else f"{order.user.username}@thesisedu.org"
    if shipping:
        first_name = (shipping.nama_penerima or order.user.username)[:50]
        phone = shipping.no_hp[:20] if shipping.no_hp else '08123456789'
        customer_details = {
            'first_name': first_name,
            'email': email,
            'phone': phone,
            'shipping_address': {
                'first_name': first_name,
                'phone': phone,
                'address': (shipping.alamat_pengiriman or '')[:100],
                'city': (shipping.kota or '')[:30],
                'postal_code': (shipping.kode_pos or '')[:10],
            }
        }
    else:
        userpengguna = getattr(order.user, 'anggota', None)
        first_name = (order.user.first_name or order.user.username)[:50]
        phone = (userpengguna.telp if userpengguna and userpengguna.telp else '08123456789')[:20]
        customer_details = {
            'first_name': first_name,
            'email': email,
            'phone': phone,
        }

    payload = {
        'transaction_details': {
            'order_id': order.order_number,
            'gross_amount': gross_amount
        },
        'item_details': item_details,
        'customer_details': customer_details,
        'callbacks': {
            'finish': f"/app/pesanan/{order.order_number}/"
        }
    }

    auth_str = base64.b64encode(f"{server_key}:".encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {auth_str}',
    }

    snap_url = get_snap_url()
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(snap_url, data=data_bytes, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_body = resp.read().decode('utf-8')
            res_data = json.loads(resp_body)
            snap_token = res_data.get('token')
            if snap_token:
                order.snap_token = snap_token
                order.save(update_fields=['snap_token'])
                return snap_token
            return None
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        logger.error(f"Midtrans Snap API HTTP Error: {e.code} - {err_msg}")
        return None
    except Exception as e:
        logger.error(f"Midtrans Snap API Error: {str(e)}")
        return None


def verify_signature(order_id, status_code, gross_amount, signature_key):
    server_key = getattr(settings, 'MIDTRANS_SERVER_KEY', '')
    raw_str = f"{order_id}{status_code}{gross_amount}{server_key}"
    calculated_hash = hashlib.sha512(raw_str.encode('utf-8')).hexdigest()
    return calculated_hash.lower() == str(signature_key).lower()


def get_api_base_url():
    if getattr(settings, 'MIDTRANS_IS_PRODUCTION', False):
        return 'https://api.midtrans.com/v2'
    return 'https://api.sandbox.midtrans.com/v2'


def check_transaction_status(order_number):
    server_key = getattr(settings, 'MIDTRANS_SERVER_KEY', '')
    if not server_key or 'YOUR_SERVER_KEY' in server_key:
        return None

    api_url = f"{get_api_base_url()}/{order_number}/status"
    auth_str = base64.b64encode(f"{server_key}:".encode('utf-8')).decode('utf-8')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_str}',
    }

    try:
        req = urllib.request.Request(api_url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode('utf-8')
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        logger.warning(f"Midtrans check status HTTP Error for {order_number}: {e.code}")
        return None
    except Exception as e:
        logger.warning(f"Midtrans check status Error for {order_number}: {str(e)}")
        return None


def sync_order_status_from_midtrans(order):
    res = check_transaction_status(order.order_number)
    if not res:
        return False, "Tidak dapat terhubung ke Midtrans atau order belum ada di Midtrans."

    transaction_status = res.get('transaction_status')
    fraud_status = res.get('fraud_status')
    payment_type = res.get('payment_type', '')
    transaction_id = res.get('transaction_id', '')

    logger.info(f"Sync order {order.order_number}: transaction_status={transaction_status}, fraud={fraud_status}")

    if transaction_status in ('capture', 'settlement'):
        if fraud_status == 'challenge':
            order.payment_status = 'pending'
            order.status = 'pending'
        else:
            order.payment_status = 'paid'
            order.status = 'processing'
            if not order.paid_at:
                order.paid_at = timezone.now()
        if payment_type:
            order.payment_type = payment_type
        if transaction_id:
            order.transaction_id = transaction_id
        order.save(update_fields=['status', 'payment_status', 'paid_at', 'payment_type', 'transaction_id'])
        order.sync_enrollments()
        return True, f"Pembayaran berhasil terverifikasi ({payment_type})."

    elif transaction_status in ('cancel', 'deny', 'expire'):
        if transaction_status == 'expire':
            order.payment_status = 'expired'
        else:
            order.payment_status = 'failed'
        order.status = 'cancelled'
        order.save(update_fields=['status', 'payment_status'])
        order.sync_enrollments()
        return True, f"Status pesanan dibatalkan ({transaction_status})."

    elif transaction_status == 'pending':
        order.payment_status = 'pending'
        if payment_type and not order.payment_type:
            order.payment_type = payment_type
            order.save(update_fields=['payment_status', 'payment_type'])
        else:
            order.save(update_fields=['payment_status'])
        return False, "Menunggu pembayaran dari pembeli."

    return False, f"Status Midtrans: {transaction_status}"


