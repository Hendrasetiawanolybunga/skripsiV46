from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Transaksi
from .tasks import send_notification_task

@receiver(post_save, sender=Transaksi)
def transaksi_status_change_handler(sender, instance, created, **kwargs):
    """
    Signal handler untuk mengirim notifikasi ketika status transaksi berubah.
    """
    # Debug logging untuk verifikasi signal tereksekusi
    print(f"--- [DEBUG Sinyal] Post_Save Transaksi #{instance.id} dipicu. Created: {created}. Status: {instance.status_transaksi} ---")
    
    # Jika ini adalah transaksi baru, tidak perlu mengirim notifikasi perubahan status
    if created:
        return
    
    # Untuk transaksi yang diupdate, periksa apakah status berubah
    try:
        # Dapatkan instance lama dari database
        old_instance = Transaksi.objects.get(pk=instance.pk)
        
        # Periksa apakah status berubah
        if old_instance.status_transaksi != instance.status_transaksi:
            # Siapkan pesan berdasarkan status baru
            status_messages = {
                'DIBAYAR': 'Pembayaran pesanan Anda telah dikonfirmasi.',
                'DIKIRIM': 'Pesanan Anda sedang dalam pengiriman.',
                'SELESAI': 'Pesanan Anda telah selesai. Terima kasih telah berbelanja!',
                'DIBATALKAN': 'Pesanan Anda telah dibatalkan.'
            }
            
            # Dapatkan pesan untuk status baru
            message = status_messages.get(instance.status_transaksi, 
                                        f'Status pesanan Anda berubah menjadi: {instance.status_transaksi}')
            
            # Untuk status SELESAI, tambahkan link untuk memberikan feedback
            if instance.status_transaksi == 'SELESAI':
                detail_url = reverse('detail_pesanan', args=[instance.pk])
                message += f" <a href='{detail_url}' class='alert-link'>Beri Feedback</a>"
            
            # Kirim notifikasi melalui Celery task
            send_notification_task.delay(
                pelanggan_id=instance.idPelanggan.id,
                tipe_pesan='Status Transaksi',
                isi_pesan=message
            )
    except Transaksi.DoesNotExist:
        # Jika tidak dapat menemukan instance lama, lewati
        pass