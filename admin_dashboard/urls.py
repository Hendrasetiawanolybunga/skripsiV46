# admin_dashboard/urls.py
from django.urls import path
from . import views
from admin_dashboard.views import custom_admin_dashboard
from .views import (
    login_karyawan,
    dashboard_karyawan,
    verifikasi_pengiriman,
    initial_setup_dummy_data,
)

urlpatterns = [
    # URLs untuk pengguna umum (public)
    path('', views.beranda_umum, name='beranda_umum'),
    path('register/', views.register_pelanggan, name='register_pelanggan'),
    path('login/', views.login_pelanggan, name='login_pelanggan'),
    path('logout/', views.logout_pelanggan, name='logout_pelanggan'),
    path('produk/public/', views.produk_list_public, name='produk_list_public'),

    # URLs untuk pelanggan yang sudah login
    # Custom admin index (do NOT use namespace-style name with colon)
    path('admin/', custom_admin_dashboard, name='admin_index_custom'),
    path('dashboard/', views.dashboard_pelanggan, name='dashboard_pelanggan'),
    path('produk/', views.produk_list, name='produk_list'),
    path('produk_detail/<int:pk>/', views.produk_detail, name='produk_detail'),
    path('keranjang/', views.keranjang, name='keranjang'),
    path('keranjang/update/<int:produk_id>/', views.update_keranjang, name='update_keranjang'),  # New URL for updating cart
    path('tambah-ke-keranjang/<int:produk_id>/', views.tambah_ke_keranjang, name='tambah_ke_keranjang'),
    path('hapus-dari-keranjang/<int:produk_id>/', views.hapus_dari_keranjang, name='hapus_dari_keranjang'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-langsung/<int:produk_id>/', views.checkout_langsung, name='checkout_langsung'),  # New URL for direct checkout
    path('proses-pembayaran/', views.proses_pembayaran, name='proses_pembayaran'),
    path('pesanan/', views.daftar_pesanan, name='daftar_pesanan'), # URL untuk halaman Pesanan
    path('pesanan/<int:pesanan_id>/', views.detail_pesanan, name='detail_pesanan'), # URL untuk detail pesanan
    path('notifikasi/', views.notifikasi, name='notifikasi'),     # URL untuk halaman Notifikasi
    path('akun/', views.akun, name='akun'),                       # URL untuk halaman Akun
    
    # URLs untuk laporan
    path('laporan/transaksi/', views.laporan_transaksi, name='laporan_transaksi'),
    path('laporan/produk-terlaris/', views.laporan_produk_terlaris, name='laporan_produk_terlaris'),
    
    # --- Karyawan Pengiriman (Non-admin interface) ---
    # Setup route (testing only)
    path('karyawan/setup/', initial_setup_dummy_data, name='initial_setup'),

    # Karyawan routes
    path('karyawan/login/', login_karyawan, name='karyawan_login'),
    path('karyawan/logout/', views.logout_karyawan, name='karyawan_logout'),
    path('karyawan/dashboard/', dashboard_karyawan, name='karyawan_dashboard'),
    path('karyawan/transaksi/<int:pk>/verifikasi/', verifikasi_pengiriman, name='verifikasi_pengiriman'),

    # (Dashboard Analitik removed) -- analytics dashboard removed from public URLs
]