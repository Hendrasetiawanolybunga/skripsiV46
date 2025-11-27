from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from datetime import date
# Model Admin (menggantikan User bawaan Django untuk admin)
class Admin(AbstractUser):
    nama_lengkap = models.CharField(max_length=255, verbose_name="Nama Lengkap")
    class Meta(AbstractUser.Meta):
        verbose_name_plural = "Admin"
        db_table = 'admin' 

# Model Pelanggan
class Pelanggan(models.Model):
    id = models.AutoField(primary_key=True)
    nama_pelanggan = models.CharField(max_length=255, verbose_name="Nama Pelanggan")
    alamat = models.TextField(verbose_name="Alamat")
    tanggal_lahir = models.DateField(verbose_name="Tanggal Lahir")
    no_hp = models.CharField(max_length=20, verbose_name="Nomor HP")
    username = models.CharField(max_length=150, unique=True, verbose_name="Username")
    password = models.CharField(max_length=128, verbose_name="Password") # Django akan menangani hash password
   
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Pelanggan"
        db_table = 'pelanggan'

    def __str__(self):
        return str(self.nama_pelanggan)


# Model Karyawan (terpisah dari model Admin)
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Karyawan(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=255, verbose_name="Nama Karyawan")
    email = models.EmailField(max_length=254, unique=True, verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Password")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Dibuat Pada")

    class Meta:
        verbose_name_plural = "Karyawan"
        db_table = 'karyawan'

    def __str__(self):
        return f"{self.nama} <{self.email}>"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def get_top_purchased_products(cls, pelanggan_id, limit=3):
        """
        Get the top purchased products for a customer
        """
        from django.db.models import Sum
        from .models import Transaksi, DetailTransaksi, Produk
        
        # Get successful transactions for this customer
        successful_transactions = Transaksi.objects.filter(
            pelanggan_id=pelanggan_id,
            status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
        )
        
        # Get top products based on quantity purchased
        top_products = DetailTransaksi.objects.filter(
            transaksi__in=successful_transactions
        ).values(
            'produk'
        ).annotate(
            total_quantity=Sum('jumlah_produk')
        ).order_by('-total_quantity')[:limit]
        
        # Extract product IDs
        product_ids = [item['produk'] for item in top_products]
        
        # Return product objects
        return Produk.objects.filter(id__in=product_ids)

# Model Kategori
class Kategori(models.Model):
    id = models.AutoField(primary_key=True)
    nama_kategori = models.CharField(max_length=255, verbose_name="Nama Kategori")

    class Meta:
        verbose_name_plural = "Kategori"
        db_table = 'kategori'

    def __str__(self):
        return str(self.nama_kategori)

# Model Produk
class Produk(models.Model):
    id = models.AutoField(primary_key=True)
    nama_produk = models.CharField(max_length=255, verbose_name="Nama Produk")
    deskripsi_produk = models.TextField(verbose_name="Deskripsi Produk")
    foto_produk = models.ImageField(upload_to='produk_images/', verbose_name="Foto Produk")
    stok_produk = models.IntegerField(verbose_name="Stok Produk")
    harga_produk = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Harga Produk")
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Kategori")

    class Meta:
        verbose_name_plural = "Produk"
        db_table = 'produk'

    def __str__(self):
        return str(self.nama_produk)

# --- Pilihan (Choices) untuk model Transaksi ---
STATUS_TRANSAKSI_CHOICES = [
    ('DIPROSES', 'Diproses'),
    ('DIBAYAR', 'Dibayar'),
    ('DIKIRIM', 'Dikirim'),
    ('SELESAI', 'Selesai'),
    ('DIBATALKAN', 'Dibatalkan'),
]

# Model Transaksi
class Transaksi(models.Model):
    id = models.AutoField(primary_key=True)
    tanggal = models.DateTimeField(default=date.today)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total", blank=True, null=True)
    ongkir = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ongkos Kirim", default=0)
    status_transaksi = models.CharField(
        max_length=50, 
        choices=STATUS_TRANSAKSI_CHOICES, 
        default='DIPROSES', 
        verbose_name="Status Transaksi"
    )
    bukti_bayar = models.FileField(upload_to='bukti_pembayaran/', verbose_name="Bukti Pembayaran", null=True, blank=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE, verbose_name="Pelanggan")
    alamat_pengiriman = models.TextField(verbose_name="Alamat Pengiriman", blank=True, null=True)
    # New fields for customer feedback
    feedback = models.TextField(verbose_name="Feedback", null=True, blank=True)
    fotofeedback = models.ImageField(upload_to='feedback_images/', verbose_name="Foto Feedback", null=True, blank=True)
    
    # New fields for payment deadline feature
    waktu_checkout = models.DateTimeField(null=True, blank=True)
    batas_waktu_bayar = models.DateTimeField(null=True, blank=True)
    foto_pengiriman = models.ImageField(
        upload_to='verifikasi_pengiriman/', 
        verbose_name="Foto Verifikasi Pengiriman", 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name_plural = "Transaksi"
        db_table = 'transaksi'

    def __str__(self):
        pelanggan_nama = getattr(self.idPelanggan, 'nama_pelanggan', 'Pelanggan')
        return f"Transaksi #{self.id} oleh {pelanggan_nama}"

# Model DetailTransaksi
class DetailTransaksi(models.Model):
    id = models.AutoField(primary_key=True)
    idTransaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE, verbose_name="Transaksi")
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE, verbose_name="Produk")
    jumlah_produk = models.IntegerField(verbose_name="Jumlah Produk")
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sub Total", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Detail Transaksi"
        db_table = 'detail_transaksi'

    def __str__(self):
        produk_nama = getattr(self.idProduk, 'nama_produk', 'Produk')
        return f"{self.jumlah_produk}x {produk_nama}"

# --- Pilihan (Choices) untuk model DiskonPelanggan ---
STATUS_DISKON_CHOICES = [
    ('aktif', 'Aktif'),
    ('tidak_aktif', 'Tidak Aktif'),
]

# Scope diskon choices
SCOPE_DISKON_CHOICES = [
    ('ALL_PRODUCTS', 'All Products'),
    ('CART_THRESHOLD', 'Cart Threshold'),
    ('SINGLE_PRODUCT', 'Single Product'),
]

# Model DiskonPelanggan
class DiskonPelanggan(models.Model):
    id = models.AutoField(primary_key=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE, verbose_name="Pelanggan")
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE, verbose_name="Produk", null=True, blank=True)
    persen_diskon = models.IntegerField(verbose_name="Persen Diskon")
    status = models.CharField(
        max_length=50, 
        choices=STATUS_DISKON_CHOICES, 
        default='aktif', 
        verbose_name="Status"
    )
    pesan = models.TextField(verbose_name="Pesan", null=True, blank=True)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Dibuat")
    
    # New fields for enhanced discount functionality
    berlaku_sampai = models.DateTimeField(null=True, blank=True, verbose_name="Berlaku Sampai")
    scope_diskon = models.CharField(
        max_length=50,
        choices=SCOPE_DISKON_CHOICES,
        default='SINGLE_PRODUCT',
        verbose_name="Scope Diskon"
    )
    minimum_cart_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Minimum Cart Total"
    )

    class Meta:
        verbose_name_plural = "Diskon Pelanggan"
        db_table = 'diskon_pelanggan'

    def __str__(self):
        pelanggan_nama = getattr(self.idPelanggan, 'nama_pelanggan', 'Pelanggan')
        return f"Diskon {self.persen_diskon}% untuk {pelanggan_nama}"

# Model Notifikasi
class Notifikasi(models.Model):
    id = models.AutoField(primary_key=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE, verbose_name="Pelanggan")
    tipe_pesan = models.CharField(max_length=50, verbose_name="Tipe Pesan")
    isi_pesan = models.TextField(verbose_name="Isi Pesan")
    is_read = models.BooleanField(default=False, verbose_name="Sudah Dibaca")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Dibuat")

    class Meta:
        verbose_name_plural = "Notifikasi"
        db_table = 'notifikasi'
    
    def __str__(self):
        pelanggan_nama = getattr(self.idPelanggan, 'nama_pelanggan', 'Pelanggan')
        return f"Notifikasi untuk {pelanggan_nama}"