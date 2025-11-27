from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Pelanggan, Notifikasi, Transaksi, DiskonPelanggan
from datetime import date
from django.db.models import Sum
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_task(pelanggan_id, tipe_pesan, isi_pesan, url_target=None):
    """
    Celery task to create a notification and send it via WebSocket
    """
    try:
        # Create notification in database
        pelanggan = Pelanggan.objects.get(id=pelanggan_id)
        
        # Add CTA URL to the message if provided
        if url_target and url_target != '#':
            isi_pesan = f"{isi_pesan} <a href='{url_target}' class='alert-link'>Lihat detail</a>"
        
        notifikasi = Notifikasi.objects.create(
            idPelanggan=pelanggan,
            tipe_pesan=tipe_pesan,
            isi_pesan=isi_pesan
        )
        
        # Send notification via WebSocket
        channel_layer = get_channel_layer()
        group_name = f"user_{pelanggan_id}"
        
        # Prepare notification data
        notification_data = {
            'id': notifikasi.id,
            'tipe_pesan': notifikasi.tipe_pesan,
            'isi_pesan': notifikasi.isi_pesan,
            'created_at': notifikasi.created_at.isoformat(),
        }
        
        # Send message to the group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'notification': notification_data
            }
        )
        
        return f"Notification sent successfully to user {pelanggan_id}"
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return f"Error sending notification: {str(e)}"

@shared_task
def check_birthday_and_loyalty_task():
    """
    Celery task to check for customers with birthdays and loyalty status
    """
    try:
        from datetime import timedelta
        today = date.today()
        
        # Find ALL customers
        all_customers = Pelanggan.objects.all()
        
        for customer in all_customers:
            # Check if customer has birthday today
            is_birthday = (
                customer.tanggal_lahir and 
                customer.tanggal_lahir.month == today.month and 
                customer.tanggal_lahir.day == today.day
            )
            
            if not is_birthday:
                continue
            
            # Calculate total spending for paid transactions
            total_spending = Transaksi.objects.filter(
                idPelanggan=customer,
                status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
            ).aggregate(
                total_belanja=Sum('total')
            )['total_belanja'] or 0
            
            # Check customer loyalty status
            is_loyal = total_spending >= 5000000
            
            # URL target for produk list page
            url_target = '/produk/'
            
            # P2-A: Loyalitas Permanen (Loyal + Birthday)
            if is_loyal:
                # Create in-app notification with CTA URL for loyal customers
                send_notification_task.delay(
                    pelanggan_id=customer.id,
                    tipe_pesan="Diskon Ulang Tahun Permanen",
                    isi_pesan="Diskon 10% otomatis aktif untuk semua produk selama 24 jam!",
                    url_target=url_target
                )
                
                # Create/update ONE discount record with scope ALL_PRODUCTS
                berlaku_sampai = today + timedelta(hours=24)
                diskon, created = DiskonPelanggan.objects.get_or_create(
                    idPelanggan=customer,
                    scope_diskon='ALL_PRODUCTS',
                    defaults={
                        'persen_diskon': 10,
                        'status': 'aktif',
                        'pesan': 'Diskon ulang tahun 10% untuk semua produk',
                        'berlaku_sampai': berlaku_sampai,
                        'scope_diskon': 'ALL_PRODUCTS'
                    }
                )
                
                if not created:
                    # Update existing discount
                    diskon.persen_diskon = 10
                    diskon.status = 'aktif'
                    diskon.pesan = 'Diskon ulang tahun 10% untuk semua produk'
                    diskon.berlaku_sampai = berlaku_sampai
                    diskon.scope_diskon = 'ALL_PRODUCTS'
                    diskon.save()
            
            # P2-B: Loyalitas Instan (Non-Loyal + Birthday)
            else:
                # Create in-app notification with CTA URL for non-loyal customers
                send_notification_task.delay(
                    pelanggan_id=customer.id,
                    tipe_pesan="Diskon Ulang Tahun Instan",
                    isi_pesan="Raih Diskon 10% untuk SEMUA belanjaan hari ini jika total keranjang Anda mencapai Rp 5.000.000.",
                    url_target=url_target
                )
                
                # Create/update ONE discount record with scope CART_THRESHOLD
                berlaku_sampai = today + timedelta(hours=24)
                diskon, created = DiskonPelanggan.objects.get_or_create(
                    idPelanggan=customer,
                    scope_diskon='CART_THRESHOLD',
                    defaults={
                        'persen_diskon': 10,
                        'status': 'aktif',
                        'pesan': 'Diskon ulang tahun 10% untuk pembelian di atas Rp 5.000.000',
                        'berlaku_sampai': berlaku_sampai,
                        'scope_diskon': 'CART_THRESHOLD',
                        'minimum_cart_total': 5000000
                    }
                )
                
                if not created:
                    # Update existing discount
                    diskon.persen_diskon = 10
                    diskon.status = 'aktif'
                    diskon.pesan = 'Diskon ulang tahun 10% untuk pembelian di atas Rp 5.000.000'
                    diskon.berlaku_sampai = berlaku_sampai
                    diskon.scope_diskon = 'CART_THRESHOLD'
                    diskon.minimum_cart_total = 5000000
                    diskon.save()
        
        return f"Birthday and loyalty check completed. Processed {all_customers.count()} customers."
    except Exception as e:
        logger.error(f"Error in birthday and loyalty check: {str(e)}")
        return f"Error in birthday and loyalty check: {str(e)}"