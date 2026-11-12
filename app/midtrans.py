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
    for item in order.items.all():
        item_details.append({
            'id': str(item.book.id if item.book else item.id)[:45],
            'price': int(item.harga_satuan),
            'quantity': int(item.quantity),
            'name': (item.judul_buku or 'Buku')[:50]
        })

    if order.ongkir and order.ongkir > 0:
        item_details.append({
            'id': 'ONGKIR',
            'price': int(order.ongkir),
            'quantity': 1,
            'name': 'Ongkos Kirim'
        })

    gross_amount = int(order.total_harga)

    email = order.user.email if (order.user and order.user.email) else f"{order.user.username}@thesisedu.org"
    customer_details = {
        'first_name': order.nama_penerima[:50],
        'email': email,
        'phone': order.no_hp[:20] if order.no_hp else '08123456789',
        'shipping_address': {
            'first_name': order.nama_penerima[:50],
            'phone': order.no_hp[:20] if order.no_hp else '08123456789',
            'address': order.alamat_pengiriman[:100],
            'city': (order.kota or '')[:30],
            'postal_code': (order.kode_pos or '')[:10],
        }
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
            order.status = 'paid'
        else:
            order.status = 'processing'
            if not order.paid_at:
                order.paid_at = timezone.now()
        if payment_type:
            order.payment_type = payment_type
        if transaction_id:
            order.transaction_id = transaction_id
        order.save(update_fields=['status', 'paid_at', 'payment_type', 'transaction_id'])
        return True, f"Pembayaran berhasil terverifikasi ({payment_type})."

    elif transaction_status in ('cancel', 'deny', 'expire'):
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        return True, f"Status pesanan dibatalkan ({transaction_status})."

    elif transaction_status == 'pending':
        if payment_type and not order.payment_type:
            order.payment_type = payment_type
            order.save(update_fields=['payment_type'])
        return False, "Menunggu pembayaran dari pembeli."

    return False, f"Status Midtrans: {transaction_status}"


