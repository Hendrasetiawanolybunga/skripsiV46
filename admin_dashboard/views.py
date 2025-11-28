from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
import logging
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .forms import PelangganRegistrationForm, PelangganLoginForm, PelangganEditForm, PembayaranForm
from .models import Produk, Pelanggan, Transaksi, DetailTransaksi, Notifikasi, DiskonPelanggan, Kategori
from django.db.models import Sum, Avg, Count, Max, Min
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
import json
import os
from django.conf import settings
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from django.contrib import admin

# Configure logger
logger = logging.getLogger(__name__)


# admin_dashboard/views.py


from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

# Pastikan model ini sudah diimpor dari .models
from .models import Transaksi, DetailTransaksi, Produk, Pelanggan # Tambahkan model yang diperlukan
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse
from django.urls import reverse
from .forms import TransaksiVerificationForm

# Tentukan ambang batas stok kritis
STOK_KRITIS_THRESHOLD = 10 
PAID_STATUSES = ['DIBAYAR', 'DIKIRIM', 'SELESAI']

# Gabungkan logika Anda dengan data yang baru
def custom_admin_dashboard(request):
    # Redirect non-staff / anonymous users to the admin login page
    try:
        if not request.user.is_authenticated or not getattr(request.user, 'is_staff', False):
            # preserve next so admin login returns here after successful auth
            return redirect(f"{reverse('admin:login')}?next={request.path}")
    except Exception:
        # If anything unexpected happens, fall back to redirect to admin login
        return redirect('admin:login')

    # 1. LOGIKA GRAFIK PENDAPATAN BULANAN (Disalin dari dashboard_analitik)
    today = timezone.now()
    monthly_revenue = []
    
    for i in range(5, -1, -1):
        start_date = (today - timedelta(days=30*i)).replace(day=1).date()
        if i == 0:
            end_date = today.date()
        else:
            next_month = (today - timedelta(days=30*(i-1))).replace(day=1).date()
            end_date = next_month - timedelta(days=1)
            
        monthly_total = Transaksi.objects.filter(
            status_transaksi__in=PAID_STATUSES,
            tanggal__date__gte=start_date, # Filter berdasarkan tanggal (date)
            tanggal__date__lte=end_date
        ).aggregate(total=Sum('total'))['total'] or 0
        
        monthly_revenue.append({
            'month': start_date.strftime('%b %Y'),
            'total': float(monthly_total) if monthly_total else 0
        })

    # 2. LOGIKA TABEL TRANSAKSI TERBARU
    latest_transactions = Transaksi.objects.filter(
        status_transaksi__in=PAID_STATUSES
    ).select_related('idPelanggan').order_by('-tanggal')[:5]

    # 3. LOGIKA TABEL PRODUK STOK MENIPIS
    low_stock_products = Produk.objects.filter(
        stok_produk__lt=STOK_KRITIS_THRESHOLD
    ).order_by('stok_produk')

    # Data untuk dikirim ke template
    context = {
        # Data untuk Chart.js
        'revenue_data_json': json.dumps(monthly_revenue),
        'chart_labels': json.dumps([item['month'] for item in monthly_revenue]),
        'chart_totals': json.dumps([item['total'] for item in monthly_revenue]),
        
        # Data untuk Tabel
        'latest_transactions': latest_transactions,
        'low_stock_products': low_stock_products,
        'stok_kritis_threshold': STOK_KRITIS_THRESHOLD,
    }
    # Sertakan context admin bawaan agar sidebar dan tautan admin tetap muncul
    try:
        admin_context = admin.site.each_context(request)
    except Exception:
        admin_context = {}

    # Gabungkan context (admin context last to ensure admin template variables exist)
    context = {**context, **admin_context}

    # Ensure admin app list is present so sidebar/menu shows available models
    try:
        app_list = admin.site.get_app_list(request)
    except Exception:
        app_list = []

    # Some templates expect 'app_list' or 'available_apps'
    context.update({'app_list': app_list, 'available_apps': app_list})

    # Template yang akan kita buat
    return render(request, 'admin_dashboard/admin_index_override.html', context)

# Untuk mengelola sesi login pelanggan
def login_required_pelanggan(view_func):
    def wrapper(request, *args, **kwargs):
        if 'pelanggan_id' in request.session:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Anda harus login untuk mengakses halaman ini.')
        return redirect('login_pelanggan')
    return wrapper

def beranda_umum(request):
    # Get gallery images from static/images/galeri
    galeri_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'galeri')
    galeri_images = []
    
    if os.path.exists(galeri_path):
        for filename in os.listdir(galeri_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                galeri_images.append(f'images/galeri/{filename}')
    
    # Get the latest 6 products from the database - using the simplest query
    produk = Produk.objects.all().order_by('-id')[:6]
    
    context = {
        'galeri_images': galeri_images[:3],  # Limit to 3 images
        'produk': produk  # Use the same variable name as in product_list.html
    }
    return render(request, 'beranda_umum.html', context)

def register_pelanggan(request):
    if request.method == 'POST':
        form = PelangganRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save the customer
                pelanggan = form.save()
                username = form.cleaned_data.get('username')
                
                # Check if customer has birthday today and send immediate notification
                from datetime import date
                today = date.today()
                is_birthday = (
                    pelanggan.tanggal_lahir and 
                    pelanggan.tanggal_lahir.month == today.month and 
                    pelanggan.tanggal_lahir.day == today.day
                )
                
                if is_birthday:
                    # Create birthday notification
                    create_notification(
                        pelanggan, 
                        "Selamat Ulang Tahun!", 
                        "Selamat ulang tahun! Nikmati diskon 10% untuk pembelanjaan hari ini. Diskon otomatis akan diterapkan saat checkout jika total belanja mencapai Rp 5.000.000.",
                        '/produk/'
                    )
                
                messages.success(request, f'Akun {username} berhasil dibuat. Silakan login untuk melanjutkan.')
                return redirect('login_pelanggan')
            except Exception as e:
                messages.error(request, 'Terjadi kesalahan saat membuat akun. Silakan coba lagi.')
        else:
            # Handle specific form errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PelangganRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_pelanggan(request):
    if request.method == 'POST':
        form = PelangganLoginForm(request.POST)
        if form.is_valid():
            try:
                pelanggan = form.pelanggan
                request.session['pelanggan_id'] = pelanggan.id
                messages.success(request, f'Selamat datang kembali, {pelanggan.nama_pelanggan}!')
                return redirect('dashboard_pelanggan')
            except Exception as e:
                messages.error(request, 'Terjadi kesalahan saat login. Silakan coba lagi.')
        else:
            # Handle form errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
            else:
                messages.error(request, 'Username atau password salah. Silakan coba lagi.')
    else:
        form = PelangganLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_pelanggan(request):
    request.session.pop('pelanggan_id', None)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('beranda_umum')

@login_required_pelanggan
def dashboard_pelanggan(request):
    pelanggan = get_object_or_404(Pelanggan, pk=request.session['pelanggan_id'])
    # Get the 3 latest products
    produk_terbaru = Produk.objects.all().order_by('-id')[:3]
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan.id)
    
    context = {
        'pelanggan': pelanggan,
        'produk_terbaru': produk_terbaru,
        'notifikasi_count': notifikasi_count
    }
    return render(request, 'dashboard_pelanggan.html', context)

def produk_list(request):
    # Get all categories for the filter UI
    kategori_list = Kategori.objects.all()
    
    # Get the selected category from the request
    kategori_id = request.GET.get('kategori')
    
    # Filter products by category if specified
    if kategori_id:
        produk = Produk.objects.filter(kategori__id=kategori_id)
    else:
        produk = Produk.objects.all()
        
    pelanggan_id = request.session.get('pelanggan_id')
    
    # Get the customer object to check birthday and total spending
    pelanggan = get_object_or_404(Pelanggan, pk=pelanggan_id) if pelanggan_id else None
    
    # Check if customer qualifies for birthday discount
    from datetime import date
    today = date.today()
    is_birthday = False
    is_loyal = False
    total_spending = 0
    
    if pelanggan:
        is_birthday = (
            pelanggan.tanggal_lahir and 
            pelanggan.tanggal_lahir.month == today.month and 
            pelanggan.tanggal_lahir.day == today.day
        )
        
        # Kondisi B: Total semua Transaksi dengan status DIBAYAR/DIKIRIM/SELESAI pelanggan tersebut ≥ Rp 5.000.000
        from django.db.models import Sum
        total_spending = Transaksi.objects.filter(
            idPelanggan=pelanggan,
            status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
        ).aggregate(
            total_belanja=Sum('total')
        )['total_belanja'] or 0
        
        is_loyal = total_spending >= 5000000
    
    # Check for P2-B: Loyalitas Instan (Non-Loyal + Birthday + Cart Total >= 5,000,000)
    qualifies_for_instant_loyalty = is_birthday and not is_loyal if pelanggan else False
    
    # Calculate total cart value before discounts for P2-B check
    total_cart_value = 0
    keranjang_belanja = request.session.get('keranjang', {}) if pelanggan else {}
    for produk_id_str, jumlah in keranjang_belanja.items():
        try:
            produk_id = int(produk_id_str)
            produk_obj = get_object_or_404(Produk, pk=produk_id)
            # Ensure all calculations use Decimal type
            harga_produk_decimal = Decimal(str(produk_obj.harga_produk))
            jumlah_decimal = Decimal(str(jumlah))
            total_cart_value += harga_produk_decimal * jumlah_decimal
        except Exception:
            pass  # Skip invalid items
    
    qualifies_for_p2b = qualifies_for_instant_loyalty and total_cart_value >= Decimal('5000000')
    
    # Customer qualifies for P2-A: Loyalitas Permanen (Loyal + Birthday)
    qualifies_for_p2a = is_birthday and is_loyal if pelanggan else False
    
    # P1: Get top purchased products for this customer
    top_products_ids = []
    if pelanggan:
        try:
            top_products = pelanggan.get_top_purchased_products(limit=3)
            top_products_ids = [p.id for p in top_products]
        except Exception:
            # Fallback if method doesn't work
            top_products_ids = []
    
    # Check for new discount scopes
    all_products_discount = None
    cart_threshold_discount = None
    if pelanggan:
        # Check for ALL_PRODUCTS discount
        all_products_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='ALL_PRODUCTS',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()
        
        # Check for CART_THRESHOLD discount
        cart_threshold_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='CART_THRESHOLD',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()
    
    # Add discount information to each product
    for p in produk:
        # Check for product-specific discount first (Priority 1)
        diskon_produk = None
        if pelanggan:
            diskon_produk = DiskonPelanggan.objects.filter(
                idPelanggan_id=pelanggan_id,
                idProduk=p,
                status='aktif'
            ).first()
            
            # If no product-specific discount, check for general discount
            if not diskon_produk:
                diskon_produk = DiskonPelanggan.objects.filter(
                    idPelanggan_id=pelanggan_id,
                    idProduk__isnull=True,  # General discount (not product-specific)
                    status='aktif'
                ).first()
        
        # If no manual discount, check for new discount scopes
        if not diskon_produk:
            # Check for ALL_PRODUCTS discount only (P2-A Loyalitas Permanen)
            # NOTE: CART_THRESHOLD (P2-B) is NOT applied at product level—it is only for cart/checkout
            if all_products_discount:
                diskon_produk = all_products_discount
        
        # P2-A: Only show birthday discount label for top 3 favorite products (Loyal + Birthday)
        if not diskon_produk and qualifies_for_p2a and p.id in top_products_ids:
            # Create a mock discount object for display purposes only
            diskon_produk = type('DiskonPelanggan', (), {
                'persen_diskon': 10,
                'pesan': 'Diskon Ulang Tahun untuk Pelanggan Loyal'
            })()
        
        # Attach discount info to product object
        p.diskon_aktif = diskon_produk
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan_id) if pelanggan_id else 0
    
    context = {
        'produk': produk,
        'kategori_list': kategori_list,
        'kategori_terpilih': kategori_id,
        'notifikasi_count': notifikasi_count,
        'qualifies_for_birthday_discount': qualifies_for_p2a  # For showing favorite product badge
    }
    return render(request, 'product_list.html', context)


# ------------------------ Karyawan Pengiriman Interface ------------------------
def karyawan_required(view_func):
    """Decorator to ensure the request has an authenticated karyawan in session."""
    def _wrapped(request, *args, **kwargs):
        karyawan_id = request.session.get('karyawan_id')
        if not karyawan_id:
            messages.error(request, 'Anda harus login sebagai karyawan untuk mengakses halaman ini.')
            return redirect('karyawan_login')
        try:
            from .models import Karyawan
            k = Karyawan.objects.get(pk=karyawan_id)
            if not k.is_active:
                messages.error(request, 'Akun karyawan tidak aktif.')
                return redirect('karyawan_login')
            request.karyawan = k
            return view_func(request, *args, **kwargs)
        except Karyawan.DoesNotExist:
            logger.warning(f'Karyawan id {karyawan_id} tidak ditemukan saat memeriksa sesi.')
            messages.error(request, 'Sesi karyawan tidak valid. Silakan login kembali.')
            return redirect('karyawan_login')
        except Exception as exc:
            logger.exception(f'Error saat memvalidasi sesi karyawan (id={karyawan_id}): {exc}')
            messages.error(request, 'Terjadi kesalahan otentikasi. Silakan login kembali.')
            return redirect('karyawan_login')
    return _wrapped


def initial_setup_dummy_data(request):
    """Create group, permissions, dummy user and a sample transaksi for testing.

    This endpoint is intended for initial setup/testing only and can be removed later.
    """
    # Create group
    group, created = Group.objects.get_or_create(name='Karyawan Pengiriman')

    # Ensure permissions exist and assign them
    try:
        ct_transaksi = ContentType.objects.get_for_model(Transaksi)
        ct_detail = ContentType.objects.get_for_model(DetailTransaksi)
        ct_produk = ContentType.objects.get_for_model(Produk)

        perm_change_transaksi = Permission.objects.get(codename='change_transaksi', content_type=ct_transaksi)
        perm_change_detail = Permission.objects.get(codename='change_detailtransaksi', content_type=ct_detail)
        perm_view_produk = Permission.objects.get(codename='view_produk', content_type=ct_produk)

        group.permissions.add(perm_change_transaksi, perm_change_detail, perm_view_produk)
    except Exception as e:
        logger.warning(f"Could not assign permissions during setup: {e}")

    # Create dummy Karyawan user (separate from Admin)
    try:
        from .models import Karyawan
        if not Karyawan.objects.filter(email='sopir1@example.com').exists():
            k = Karyawan(nama='Budi Kurir', email='sopir1@example.com')
            k.set_password('sopir123')
            k.save()
    except Exception as e:
        logger.warning(f"Could not create karyawan during setup: {e}")

    # Create dummy Pelanggan, Produk and Transaksi (if none exist)
    try:
        pelanggan, _ = Pelanggan.objects.get_or_create(
            username='pelanggan_dummy',
            defaults={
                'nama_pelanggan': 'Pelanggan Dummy',
                'alamat': 'Jl. Contoh No.1',
                'tanggal_lahir': timezone.now().date(),
                'no_hp': '08123456789',
                'password': 'dummy'
            }
        )

        produk, _ = Produk.objects.get_or_create(
            nama_produk='Produk Dummy',
            defaults={'deskripsi_produk': 'Produk untuk testing', 'stok_produk': 100, 'harga_produk': Decimal('10000.00')}
        )

        if not Transaksi.objects.filter(status_transaksi='DIKIRIM').exists():
            transaksi = Transaksi.objects.create(
                idPelanggan=pelanggan,
                total=Decimal('10000.00'),
                status_transaksi='DIKIRIM',
                alamat_pengiriman='Jl. Contoh No.1'
            )
            DetailTransaksi.objects.create(idTransaksi=transaksi, idProduk=produk, jumlah_produk=1, sub_total=Decimal('10000.00'))
    except Exception as e:
        logger.warning(f"Could not create dummy transaksi during setup: {e}")

    messages.success(request, 'Initial setup selesai (group, permissions, dummy user, transaksi).')
    return redirect('karyawan_login')


def login_karyawan(request):
    """Login view for delivery staff using the separate Karyawan model and session-based auth."""
    from .forms import KaryawanLoginForm
    if request.method == 'POST':
        form = KaryawanLoginForm(request.POST)
        if form.is_valid():
            k = form.karyawan
            request.session['karyawan_id'] = k.id
            # Ensure session is persisted immediately
            try:
                request.session.save()
            except Exception:
                # Fallback: mark as modified
                request.session.modified = True
            logger.info(f'Karyawan {k.email} (id={k.id}) logged in; session saved.')
            messages.success(request, f'Selamat datang, {k.nama}!')
            return redirect('karyawan_dashboard')
        else:
            # Show validation errors
            for err in form.non_field_errors():
                messages.error(request, err)
            form = form
    else:
        form = KaryawanLoginForm()
    return render(request, 'karyawan/login.html', {'form': form})


@karyawan_required
def dashboard_karyawan(request):
    # Show transaksi with status 'DIKIRIM'
    kirim_list = Transaksi.objects.filter(status_transaksi='DIKIRIM').select_related('idPelanggan').order_by('-tanggal')
    context = {'transaksi_list': kirim_list, 'karyawan': getattr(request, 'karyawan', None)}
    return render(request, 'karyawan/dashboard.html', context)


@karyawan_required
def verifikasi_pengiriman(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    if request.method == 'POST':
        form = TransaksiVerificationForm(request.POST, request.FILES, instance=transaksi)
        if form.is_valid():
            obj = form.save(commit=False)
            # If status set to SELESAI, ensure foto_pengiriman saved
            if obj.status_transaksi == 'SELESAI' and not obj.foto_pengiriman:
                messages.error(request, 'Mohon upload foto pengiriman sebelum menyelesaikan.')
            else:
                obj.save()
                messages.success(request, 'Verifikasi pengiriman disimpan.')
                return redirect('karyawan_dashboard')
    else:
        form = TransaksiVerificationForm(instance=transaksi)
    # Render the verification form inside an aesthetic card on the karyawan dashboard
    return render(request, 'karyawan/verifikasi.html', {'form': form, 'transaksi': transaksi, 'karyawan': getattr(request, 'karyawan', None)})


def logout_karyawan(request):
    """Logout untuk karyawan (session-based)."""
    request.session.pop('karyawan_id', None)
    messages.success(request, 'Anda berhasil logout.')
    return redirect('karyawan_login')

# ---------------------- end of Karyawan Pengiriman Interface --------------------

def produk_list_public(request):
    # Get all categories for the filter UI
    kategori_list = Kategori.objects.all()
    
    # Get the selected category from the request
    kategori_id = request.GET.get('kategori')
    
    # Filter products by category if specified
    if kategori_id:
        produk = Produk.objects.filter(kategori__id=kategori_id)
    else:
        produk = Produk.objects.all()
    
    # Add discount information to each product (for display purposes only)
    for p in produk:
        # Check for any active discount (no customer-specific filtering for public view)
        diskon_produk = DiskonPelanggan.objects.filter(
            idProduk=p,
            status='aktif'
        ).first()
        
        # If no product-specific discount, check for general discount
        if not diskon_produk:
            diskon_produk = DiskonPelanggan.objects.filter(
                idProduk__isnull=True,  # General discount
                status='aktif'
            ).first()
        
        # Attach discount info to product object
        p.diskon_aktif = diskon_produk
    
    context = {
        'produk': produk,
        'kategori_list': kategori_list,
        'kategori_terpilih': kategori_id
    }
    return render(request, 'product_list_public.html', context)


def produk_detail(request, pk):
    # Get the product
    produk = get_object_or_404(Produk, pk=pk)
    
    # Get all categories for the filter UI
    kategori_list = Kategori.objects.all()
    
    context = {
        'produk': produk,
        'kategori_list': kategori_list
    }
    return render(request, 'product_detail.html', context)

@login_required_pelanggan
def keranjang(request):
    keranjang_belanja = request.session.get('keranjang', {})
    produk_di_keranjang = []
    total_belanja = 0
    total_sebelum_diskon = 0
    total_diskon = 0

    pelanggan_id = request.session.get('pelanggan_id')
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan_id)
    
    # Get the customer object to check birthday and total spending
    pelanggan = get_object_or_404(Pelanggan, pk=pelanggan_id)
    
    # Check if customer qualifies for birthday discount
    # Kondisi A: Tanggal Lahir == Tanggal Hari Ini
    from datetime import date
    today = date.today()
    is_birthday = (
        pelanggan.tanggal_lahir and 
        pelanggan.tanggal_lahir.month == today.month and 
        pelanggan.tanggal_lahir.day == today.day
    )
    
    # Kondisi B: Total semua Transaksi dengan status DIBAYAR/DIKIRIM/SELESAI pelanggan tersebut ≥ Rp 5.000.000
    from django.db.models import Sum
    total_spending = Transaksi.objects.filter(
        idPelanggan=pelanggan,
        status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
    ).aggregate(
        total_belanja=Sum('total')
    )['total_belanja'] or 0
    
    is_loyal = total_spending >= 5000000
    
    # Check for P2-B: Loyalitas Instan (Birthday + Cart Total >= 5,000,000)
    # Calculate total cart value before discounts for P2-B check
    total_cart_value = 0
    for produk_id_str, jumlah in keranjang_belanja.items():
        try:
            produk_id = int(produk_id_str)
            produk = get_object_or_404(Produk, pk=produk_id)
            # Ensure all calculations use Decimal type
            harga_produk_decimal = Decimal(str(produk.harga_produk))
            jumlah_decimal = Decimal(str(jumlah))
            total_cart_value += harga_produk_decimal * jumlah_decimal
        except Exception:
            pass  # Skip invalid items
    
    # P2-B eligibility: Birthday + Cart Total >= 5,000,000 (regardless of loyalty status)
    qualifies_for_p2b = is_birthday and total_cart_value >= Decimal('5000000')
    
    # Birthday notifications are now handled by the management command
    # No need to trigger them from the cart view
    
    # Check for new discount scopes
    all_products_discount = None
    cart_threshold_discount = None
    if pelanggan_id:
        # Check for ALL_PRODUCTS discount
        all_products_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='ALL_PRODUCTS',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()
        
        # Check for CART_THRESHOLD discount
        cart_threshold_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='CART_THRESHOLD',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()

    for produk_id, jumlah in keranjang_belanja.items():
        produk = get_object_or_404(Produk, pk=produk_id)
        harga_asli = produk.harga_produk * jumlah
        sub_total = harga_asli
        
        # Check for discounts
        diskon = None
        potongan_harga = 0
        harga_setelah_diskon = sub_total
        
        # Check for product-specific discount first
        diskon_produk = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            idProduk=produk,
            status='aktif'
        ).first()
        
        # If no product-specific discount, check for general discount
        if not diskon_produk:
            diskon_produk = DiskonPelanggan.objects.filter(
                idPelanggan_id=pelanggan_id,
                idProduk__isnull=True,  # General discount
                status='aktif'
            ).first()
        
        # If no manual discount, check for new discount scopes
        if not diskon_produk:
            # Check for ALL_PRODUCTS discount
            if all_products_discount:
                diskon_produk = all_products_discount
            # Check for CART_THRESHOLD discount (only apply if cart meets threshold)
            elif cart_threshold_discount and total_cart_value >= (cart_threshold_discount.minimum_cart_total or Decimal('0')):
                diskon_produk = cart_threshold_discount
        
        # Birthday discount logic has been moved to the checkout process
        # No birthday discount applied in the cart view
        
        if diskon_produk:
            diskon = diskon_produk
            # Ensure all calculations use Decimal type
            sub_total_decimal = Decimal(str(sub_total))
            persen_diskon_decimal = Decimal(str(diskon.persen_diskon))
            potongan_harga = int(sub_total_decimal * (persen_diskon_decimal / 100))
            harga_setelah_diskon = sub_total_decimal - Decimal(str(potongan_harga))
            sub_total = harga_setelah_diskon
        
        total_belanja += sub_total
        total_sebelum_diskon += harga_asli
        total_diskon += potongan_harga
        
        produk_di_keranjang.append({
            'produk': produk,
            'jumlah': jumlah,
            'sub_total': sub_total,
            'harga_asli': harga_asli,
            'diskon': diskon,
            'potongan_harga': potongan_harga,
            'harga_setelah_diskon': harga_setelah_diskon
        })

    context = {
        'produk_di_keranjang': produk_di_keranjang,
        'total_belanja': total_belanja,
        'total_sebelum_diskon': total_sebelum_diskon,
        'total_diskon': total_diskon,
        'total_setelah_diskon': total_sebelum_diskon - total_diskon,
        'notifikasi_count': notifikasi_count,
        'is_birthday': is_birthday,
        'is_loyal': is_loyal,
        'total_spending': total_spending,
        'qualifies_for_p2b': qualifies_for_p2b,  # For showing P2-B eligibility in cart
        'total_cart_value': total_cart_value  # For showing cart value in cart
    }
    return render(request, 'keranjang.html', context)

@login_required_pelanggan
def tambah_ke_keranjang(request, produk_id):
    produk = get_object_or_404(Produk, pk=produk_id)
    jumlah = int(request.POST.get('jumlah', 1))

    if jumlah <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Jumlah produk harus lebih dari 0.'})
        messages.error(request, 'Jumlah produk harus lebih dari 0.')
        return redirect('produk_list')

    keranjang_belanja = request.session.get('keranjang', {})
    produk_id_str = str(produk.pk)
    
    # Validate stock availability before adding to cart
    current_jumlah_in_cart = keranjang_belanja.get(produk_id_str, 0)
    total_requested = current_jumlah_in_cart + jumlah
    
    if total_requested > produk.stok_produk:
        # If requested quantity exceeds stock, adjust to available stock
        available_stock = produk.stok_produk - current_jumlah_in_cart
        if available_stock <= 0:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Stok produk {produk.nama_produk} tidak mencukupi.'})
            messages.error(request, f'Stok produk {produk.nama_produk} tidak mencukupi.')
            return redirect('produk_list')
        else:
            # Adjust quantity to available stock
            jumlah = available_stock
            messages.warning(request, f'Stok produk {produk.nama_produk} tidak mencukupi. Jumlah yang bisa ditambahkan: {jumlah}.')
    
    if produk_id_str in keranjang_belanja:
        keranjang_belanja[produk_id_str] += jumlah
    else:
        keranjang_belanja[produk_id_str] = jumlah
    
    request.session['keranjang'] = keranjang_belanja
    
    # Calculate total items in cart
    total_keranjang = sum(keranjang_belanja.values())
    
    # Check if customer qualifies for birthday discount and send notification if not already sent
    pelanggan_id = request.session.get('pelanggan_id')
    if pelanggan_id:
        pelanggan = get_object_or_404(Pelanggan, pk=pelanggan_id)
        
        # Check if customer has birthday today
        from datetime import date
        today = date.today()
        is_birthday = (
            pelanggan.tanggal_lahir and 
            pelanggan.tanggal_lahir.month == today.month and 
            pelanggan.tanggal_lahir.day == today.day
        )
        
        if is_birthday:
            # Check if customer has already received a birthday notification today
            existing_notification = Notifikasi.objects.filter(
                idPelanggan=pelanggan,
                tipe_pesan__in=["Selamat Ulang Tahun!", "Diskon Ulang Tahun Permanen", "Diskon Ulang Tahun Instan"],
                created_at__date=today
            ).first()
            
            # If no birthday notification sent today, create one
            if not existing_notification:
                # Calculate total spending for paid transactions
                from django.db.models import Sum
                total_spending = Transaksi.objects.filter(
                    idPelanggan=pelanggan,
                    status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
                ).aggregate(
                    total_belanja=Sum('total')
                )['total_belanja'] or 0
                
                # Check customer loyalty status
                is_loyal = total_spending >= 5000000
                
                # Send appropriate notification based on loyalty status
                if is_loyal:
                    # P2-A: Loyalitas Permanen (Loyal + Birthday)
                    create_notification(
                        pelanggan,
                        "Diskon Ulang Tahun Permanen",
                        "Selamat ulang tahun! Diskon 10% otomatis aktif pada 3 produk terfavorit Anda.",
                        '/produk/'
                    )
                else:
                    # P2-B: Loyalitas Instan (Non-Loyal + Birthday)
                    create_notification(
                        pelanggan,
                        "Diskon Ulang Tahun Instan",
                        "Selamat ulang tahun! Raih Diskon 10% untuk SEMUA belanjaan hari ini jika total keranjang Anda mencapai Rp 5.000.000.",
                        '/produk/'
                    )
    
    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{jumlah} {produk.nama_produk} berhasil ditambahkan ke keranjang.',
            'cart_total_items': total_keranjang
        })
    
    # Handle regular request (fallback)
    messages.success(request, f'{jumlah} {produk.nama_produk} berhasil ditambahkan ke keranjang.')
    return redirect('produk_list')

@login_required_pelanggan
def hapus_dari_keranjang(request, produk_id):
    keranjang_belanja = request.session.get('keranjang', {})
    produk_id_str = str(produk_id)

    if produk_id_str in keranjang_belanja:
        del keranjang_belanja[produk_id_str]
        request.session['keranjang'] = keranjang_belanja
        messages.success(request, 'Produk berhasil dihapus dari keranjang.')
    
    return redirect('keranjang')

@login_required_pelanggan
def update_keranjang(request, produk_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        keranjang_belanja = request.session.get('keranjang', {})
        produk_id_str = str(produk_id)
        
        if produk_id_str in keranjang_belanja:
            produk = get_object_or_404(Produk, pk=produk_id)
            current_jumlah = keranjang_belanja[produk_id_str]
            
            if action == 'increase':
                # Check if we can increase (stock availability)
                if current_jumlah < produk.stok_produk:
                    keranjang_belanja[produk_id_str] = current_jumlah + 1
                    messages.success(request, f'Jumlah {produk.nama_produk} berhasil diperbarui.')
                else:
                    messages.warning(request, f'Stok produk {produk.nama_produk} tidak mencukupi. Jumlah maksimal: {produk.stok_produk}.')
            elif action == 'decrease':
                if current_jumlah > 1:
                    keranjang_belanja[produk_id_str] = current_jumlah - 1
                    messages.success(request, f'Jumlah {produk.nama_produk} berhasil diperbarui.')
                else:
                    # Remove item if quantity would be zero
                    del keranjang_belanja[produk_id_str]
                    messages.success(request, f'{produk.nama_produk} berhasil dihapus dari keranjang.')
            
            request.session['keranjang'] = keranjang_belanja
        
        return redirect('keranjang')
    
    return redirect('keranjang')

@login_required_pelanggan
def checkout(request):
    pelanggan_id = request.session.get('pelanggan_id')
    keranjang_belanja = request.session.get('keranjang', {})
    
    # Debug: Log cart contents
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Checkout initiated for customer {pelanggan_id} with cart: {keranjang_belanja}")

    if not keranjang_belanja:
        messages.error(request, 'Keranjang belanja Anda kosong, tidak dapat melakukan checkout.')
        return redirect('produk_list')

    # Store cart data in session for later use in payment processing
    request.session['checkout_data'] = {
        'keranjang_belanja': keranjang_belanja,
        'timestamp': timezone.now().isoformat()
    }
    
    # Redirect directly to payment page instead of showing modal
    return redirect('proses_pembayaran')

@login_required_pelanggan
def checkout_langsung(request, produk_id):
    if request.method == 'POST':
        produk = get_object_or_404(Produk, pk=produk_id)
        jumlah = int(request.POST.get('jumlah', 1))
        
        if jumlah <= 0:
            messages.error(request, 'Jumlah produk harus lebih dari 0.')
            return redirect('produk_list')
        
        if produk.stok_produk < jumlah:
            # Adjust quantity to available stock
            old_jumlah = jumlah
            jumlah = produk.stok_produk
            if jumlah == 0:
                messages.error(request, f'Produk {produk.nama_produk} tidak tersedia saat ini (stok habis).')
                return redirect('produk_list')
            else:
                messages.warning(request, f'Stok produk {produk.nama_produk} tidak mencukupi. Jumlah yang bisa dibeli: {jumlah} (dari {old_jumlah}).')
                # Update the quantity in the POST data for consistency
                request.POST = request.POST.copy()
                request.POST['jumlah'] = str(jumlah)
        
        # Create a temporary cart with just this product
        keranjang_belanja = {str(produk_id): jumlah}
        
        # Store cart data in session for payment processing
        request.session['checkout_data'] = {
            'keranjang_belanja': keranjang_belanja,
            'timestamp': timezone.now().isoformat()
        }
        
        # Redirect directly to payment page instead of showing modal
        return redirect('proses_pembayaran')
    
    return redirect('produk_list')

@login_required_pelanggan
def proses_pembayaran(request):
    # Debug: Log request method and POST data
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"proses_pembayaran called with method: {request.method}")
    logger.info(f"POST data: {request.POST}")
    logger.info(f"FILES data: {request.FILES}")
    
    if request.method == 'POST':
        form = PembayaranForm(request.POST, request.FILES)
        if form.is_valid():
            # Retrieve cart data from session
            checkout_data = request.session.get('checkout_data', {})
            keranjang_belanja = checkout_data.get('keranjang_belanja', {})
            
            # Also check regular cart if checkout_data is empty (fallback)
            if not keranjang_belanja:
                keranjang_belanja = request.session.get('keranjang', {})
            
            if not keranjang_belanja:
                # Only show this message if it's not a GET request or if there's a real issue
                # For GET requests, we should not show error messages
                if request.method == 'POST':
                    messages.error(request, 'Data checkout tidak ditemukan. Silakan coba lagi.')
                return redirect('keranjang')
            
            pelanggan_id = request.session.get('pelanggan_id')
            pelanggan = get_object_or_404(Pelanggan, pk=pelanggan_id)
            total_belanja = 0

            try:
                with transaction.atomic():
                    # Get the shipping address from the form or use customer's default address
                    alamat_pengiriman = request.POST.get('alamat_pengiriman', '').strip()
                    if not alamat_pengiriman:
                        alamat_pengiriman = pelanggan.alamat
                    
                    transaksi = Transaksi.objects.create(
                        idPelanggan=pelanggan,
                        tanggal=timezone.now(),
                        total=0,
                        bukti_bayar=request.FILES.get('bukti_bayar'),
                        status_transaksi='DIPROSES',
                        alamat_pengiriman=alamat_pengiriman
                    )
                    
                    # SET WAKTU BATAS JIKA BELUM ADA
                    if not transaksi.batas_waktu_bayar:
                        transaksi.waktu_checkout = timezone.now()
                        # Tentukan batas waktu pembayaran 24 jam ke depan
                        transaksi.batas_waktu_bayar = transaksi.waktu_checkout + timedelta(hours=24) 
                        transaksi.save()
                    
                    detail_list = []  # To store details for later use
                    
                    # P1: Get top purchased products for this customer
                    try:
                        top_products = pelanggan.get_top_purchased_products(limit=3)
                        top_products_ids = [p.id for p in top_products]
                    except Exception:
                        # Fallback if method doesn't work
                        top_products_ids = []
                    
                    # Check if customer qualifies for birthday discount
                    from datetime import date
                    today = date.today()
                    is_birthday = (
                        pelanggan.tanggal_lahir and 
                        pelanggan.tanggal_lahir.month == today.month and 
                        pelanggan.tanggal_lahir.day == today.day
                    )
                    
                    # Kondisi B: Total semua Transaksi dengan status DIBAYAR/DIKIRIM/SELESAI pelanggan tersebut ≥ Rp 5.000.000
                    from django.db.models import Sum
                    total_spending = Transaksi.objects.filter(
                        idPelanggan=pelanggan,
                        status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
                    ).aggregate(
                        total_belanja=Sum('total')
                    )['total_belanja'] or 0
                    
                    is_loyal = total_spending >= 5000000
                    
                    # Calculate total cart value before discounts for P2-B check
                    total_cart_value = 0
                    for produk_id_str, jumlah in keranjang_belanja.items():
                        produk_id = int(produk_id_str)
                        produk = get_object_or_404(Produk, pk=produk_id)
                        # Ensure all calculations use Decimal type
                        harga_produk_decimal = Decimal(str(produk.harga_produk))
                        jumlah_decimal = Decimal(str(jumlah))
                        total_cart_value += harga_produk_decimal * jumlah_decimal
                    
                    # Check for P2-B: Universal Birthday Discount (Birthday + Cart Total >= 5,000,000)
                    # Logic: Ulang Tahun HARI INI AND Total Keranjang >= Rp 5000000
                    is_p2b_eligible = (
                        is_birthday and 
                        total_cart_value >= Decimal('5000000')
                    )
                    
                    # Customer qualifies for P2-A: Loyalitas Permanen (Loyal + Birthday)
                    qualifies_for_p2a = is_birthday and is_loyal
                    
                    # Check for new discount scopes
                    all_products_discount = DiskonPelanggan.objects.filter(
                        idPelanggan_id=pelanggan_id,
                        scope_diskon='ALL_PRODUCTS',
                        status='aktif',
                        berlaku_sampai__gte=timezone.now()
                    ).first()
                    
                    cart_threshold_discount = DiskonPelanggan.objects.filter(
                        idPelanggan_id=pelanggan_id,
                        scope_diskon='CART_THRESHOLD',
                        status='aktif',
                        berlaku_sampai__gte=timezone.now()
                    ).first()
                    
                    # Validate stock for all items in cart before processing payment
                    adjusted_items = []
                    items_to_remove = []
                    
                    for produk_id_str, jumlah in keranjang_belanja.items():
                        produk_id = int(produk_id_str)
                        produk = get_object_or_404(Produk, pk=produk_id)
                        
                        if produk.stok_produk < jumlah:
                            # Adjust quantity to available stock
                            old_jumlah = jumlah
                            jumlah = produk.stok_produk
                            keranjang_belanja[produk_id_str] = jumlah
                            messages.warning(request, f'Stok produk {produk.nama_produk} tidak mencukupi. Jumlah yang bisa dibeli: {jumlah} (dari {old_jumlah}).')
                            
                            # If stock is 0, mark item for removal
                            if jumlah == 0:
                                items_to_remove.append(produk_id_str)
                                messages.warning(request, f'Produk {produk.nama_produk} telah dihapus dari keranjang karena stok habis.')
                                continue
                        
                        adjusted_items.append((produk_id_str, jumlah))
                    
                    # Remove items with zero stock
                    for item_id in items_to_remove:
                        if item_id in keranjang_belanja:
                            del keranjang_belanja[item_id]
                    
                    # Check if cart is empty after stock validation
                    if not keranjang_belanja:
                        messages.error(request, 'Keranjang belanja Anda kosong setelah penyesuaian stok. Silakan tambahkan produk lain.')
                        return redirect('keranjang')
                    
                    # Update session with adjusted cart
                    request.session['keranjang'] = keranjang_belanja
                    if 'checkout_data' in request.session:
                        request.session['checkout_data']['keranjang_belanja'] = keranjang_belanja
                    
                    # Process items with validated stock
                    for produk_id_str, jumlah in adjusted_items:
                        produk_id = int(produk_id_str)
                        produk = get_object_or_404(Produk, pk=produk_id)
                        
                        # Final check after adjustments
                        if produk.stok_produk < jumlah:
                            raise ValueError(f'Stok produk {produk.nama_produk} tidak mencukupi. Hanya tersisa {produk.stok_produk}.')
                        
                        # Calculate price with discount if applicable
                        harga_satuan = produk.harga_produk
                        
                        # Check for product-specific discount first (Priority 1)
                        diskon_produk = DiskonPelanggan.objects.filter(
                            idPelanggan_id=pelanggan_id,
                            idProduk=produk,
                            status='aktif'
                        ).first()
                        
                        # If no product-specific discount, check for general discount
                        if not diskon_produk:
                            diskon_produk = DiskonPelanggan.objects.filter(
                                idPelanggan_id=pelanggan_id,
                                idProduk__isnull=True,  # General discount
                                status='aktif'
                            ).first()
                        
                        # If no manual discount, check for new discount scopes
                        if not diskon_produk:
                            # Check for ALL_PRODUCTS discount only (P2-A Loyalitas Permanen)
                            # NOTE: CART_THRESHOLD (P2-B) is NOT applied per-item — it's applied to total cart only
                            if all_products_discount:
                                diskon_produk = all_products_discount
                        
                        # If no manual discount found, check for birthday discounts (Priority 2)
                        if not diskon_produk:
                            # P2-A: Loyalitas Permanen - Apply 10% discount to top 3 favorite products
                            if qualifies_for_p2a and produk_id in top_products_ids:
                                # Apply 10% birthday discount
                                harga_satuan_decimal = Decimal(str(harga_satuan))
                                persen_diskon_decimal = Decimal('10')
                                harga_satuan = harga_satuan_decimal - (harga_satuan_decimal * persen_diskon_decimal / 100)
                            
                            # P2-B: Loyalitas Instan — NOT applied per-item; will be applied to cart total after loop
                        
                        # Apply manual discount if found (Priority 1)
                        elif diskon_produk:
                            # Ensure all calculations use Decimal type
                            harga_satuan_decimal = Decimal(str(harga_satuan))
                            persen_diskon_decimal = Decimal(str(diskon_produk.persen_diskon))
                            harga_satuan = harga_satuan_decimal - (harga_satuan_decimal * persen_diskon_decimal / 100)
                        
                        # Save the original stock before updating
                        produk.stok_produk -= jumlah
                        produk.save()
                        
                        # Ensure all calculations use Decimal type
                        harga_satuan_decimal = Decimal(str(harga_satuan))
                        jumlah_decimal = Decimal(str(jumlah))
                        sub_total = harga_satuan_decimal * jumlah_decimal
                        detail = DetailTransaksi.objects.create(
                            idTransaksi=transaksi,
                            idProduk=produk,
                            jumlah_produk=jumlah,
                            sub_total=sub_total
                        )
                        detail_list.append(detail)
                        total_belanja += sub_total

                    # P2-B: Apply 10% discount to total cart (NOT per-item)
                    # If customer qualifies for P2-B and CART_THRESHOLD is active, apply discount to total
                    if is_p2b_eligible and cart_threshold_discount:
                        potongan_p2b = total_belanja * Decimal('10') / Decimal('100')
                        total_belanja -= potongan_p2b

                    transaksi.total = total_belanja
                    transaksi.save()

                    # Clear cart and checkout data from session
                    request.session.pop('keranjang', None)
                    request.session.pop('checkout_data', None)

                    # Create notification for the customer
                    create_notification(
                        pelanggan, 
                        "Pesanan Baru", 
                        f"Pesanan Anda telah berhasil dibuat. Silakan tunggu konfirmasi dari admin. Nomor pesanan: #{transaksi.id}"
                    )

                    messages.success(request, 'Pembayaran berhasil! Terima kasih telah berbelanja.')
                    return redirect('daftar_pesanan')

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('keranjang')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan saat memproses pembayaran: {e}')
                return redirect('keranjang')
        else:
            # Form is not valid, show errors
            # Only show this message if there are actual form errors
            if form.errors:
                # Debug: Log the specific form errors
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Form validation errors: {form.errors}")
                
                # Display specific error messages to the user
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                messages.error(request, f"Terjadi kesalahan dalam pengisian form pembayaran: {'; '.join(error_messages)}")
            else:
                # If form is not valid but has no errors, it might be a GET request
                # Don't show error message in this case
                pass
    # For both GET requests and invalid form submissions, show the payment form
    # GET request - show payment form
    logger.info(f"Showing payment form for GET request or invalid form submission")
    form = PembayaranForm()
    
    # Retrieve cart data for displaying in the form
    checkout_data = request.session.get('checkout_data', {})
    keranjang_belanja = checkout_data.get('keranjang_belanja', {})
    
    # Also check regular cart if checkout_data is empty (fallback)
    if not keranjang_belanja:
        keranjang_belanja = request.session.get('keranjang', {})
    
    if not keranjang_belanja:
        # Only show this message if it's not a GET request or if there's a real issue
        # For GET requests, we should not show error messages
        if request.method == 'POST':
            messages.error(request, 'Data keranjang tidak ditemukan. Silakan tambahkan produk ke keranjang terlebih dahulu.')
        return redirect('keranjang')
    
    total_belanja = 0
    total_sebelum_diskon = 0
    total_diskon = 0
    produk_di_keranjang = []
    
    pelanggan_id = request.session.get('pelanggan_id')
    pelanggan = get_object_or_404(Pelanggan, pk=pelanggan_id)
    
    # Create a temporary transaction to set payment deadline
    transaksi = Transaksi(
        idPelanggan=pelanggan,
        total=0,
        status_transaksi='DIPROSES'
    )
    
    # SET WAKTU BATAS JIKA BELUM ADA
    if not transaksi.batas_waktu_bayar:
        transaksi.waktu_checkout = timezone.now()
        # Tentukan batas waktu pembayaran 24 jam ke depan
        transaksi.batas_waktu_bayar = transaksi.waktu_checkout + timedelta(hours=24)

    # --- Prepare discount/context variables (same logic as POST path) ---
    # Ensure variables used later in template are always defined to avoid UnboundLocalError
    try:
        # P1: Get top purchased products for this customer
        try:
            top_products = pelanggan.get_top_purchased_products(limit=3)
            top_products_ids = [p.id for p in top_products]
        except Exception:
            top_products_ids = []

        # Check if customer qualifies for birthday discount
        from datetime import date
        today = date.today()
        is_birthday = (
            pelanggan.tanggal_lahir and
            pelanggan.tanggal_lahir.month == today.month and
            pelanggan.tanggal_lahir.day == today.day
        )

        # Kondisi Loyalitas: Total transaksi tertentu
        from django.db.models import Sum
        total_spending = Transaksi.objects.filter(
            idPelanggan=pelanggan,
            status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
        ).aggregate(total_belanja=Sum('total'))['total_belanja'] or 0

        is_loyal = total_spending >= 5000000

        # Calculate total cart value before discounts for P2-B check
        total_cart_value = Decimal('0')
        for produk_id_str, jumlah in keranjang_belanja.items():
            try:
                produk_id_tmp = int(produk_id_str)
                produk_tmp = get_object_or_404(Produk, pk=produk_id_tmp)
                harga_produk_decimal = Decimal(str(produk_tmp.harga_produk))
                jumlah_decimal = Decimal(str(jumlah))
                total_cart_value += harga_produk_decimal * jumlah_decimal
            except Exception:
                pass

        qualifies_for_p2a = is_birthday and is_loyal

        # Check for new discount scopes
        all_products_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='ALL_PRODUCTS',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()

        cart_threshold_discount = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            scope_diskon='CART_THRESHOLD',
            status='aktif',
            berlaku_sampai__gte=timezone.now()
        ).first()
    except Exception:
        # Defensive defaults in case any lookup fails
        top_products_ids = []
        total_cart_value = Decimal('0')
        qualifies_for_p2a = False
        all_products_discount = None
        cart_threshold_discount = None
    
    for produk_id_str, jumlah in keranjang_belanja.items():
        produk_id = int(produk_id_str)
        produk = get_object_or_404(Produk, pk=produk_id)
        # Ensure all calculations use Decimal type
        harga_produk_decimal = Decimal(str(produk.harga_produk))
        jumlah_decimal = Decimal(str(jumlah))
        harga_asli = harga_produk_decimal * jumlah_decimal
        sub_total = harga_asli
        
        # Check for discounts
        diskon = None
        potongan_harga = 0
        harga_setelah_diskon = sub_total
        
        # Check for product-specific discount first
        diskon_produk = DiskonPelanggan.objects.filter(
            idPelanggan_id=pelanggan_id,
            idProduk=produk,
            status='aktif'
        ).first()
        
        # If no product-specific discount, check for general discount
        if not diskon_produk:
            diskon_produk = DiskonPelanggan.objects.filter(
                idPelanggan_id=pelanggan_id,
                idProduk__isnull=True,  # General discount
                status='aktif'
            ).first()
        
        # If no manual discount, check for new discount scopes
        if not diskon_produk:
            # Check for ALL_PRODUCTS discount
            if all_products_discount:
                diskon_produk = all_products_discount
            # Check for CART_THRESHOLD discount (only apply if cart meets threshold)
            elif cart_threshold_discount and total_cart_value >= (cart_threshold_discount.minimum_cart_total or Decimal('0')):
                diskon_produk = cart_threshold_discount
        
        if diskon_produk:
            diskon = diskon_produk
            # Ensure all calculations use Decimal type
            sub_total_decimal = Decimal(str(sub_total))
            persen_diskon_decimal = Decimal(str(diskon.persen_diskon))
            potongan_harga = int(sub_total_decimal * (persen_diskon_decimal / 100))
            harga_setelah_diskon = sub_total_decimal - Decimal(str(potongan_harga))
            sub_total = harga_setelah_diskon
        
        total_belanja += sub_total
        total_sebelum_diskon += harga_asli
        total_diskon += potongan_harga
        
        produk_di_keranjang.append({
            'produk': produk,
            'jumlah': jumlah,
            'sub_total': sub_total,
            'harga_asli': harga_asli,
            'diskon': diskon,
            'potongan_harga': potongan_harga,
            'harga_setelah_diskon': harga_setelah_diskon
        })

    context = {
        'form': form,
        'produk_di_keranjang': produk_di_keranjang,
        'total_belanja': total_belanja,
        'total_sebelum_diskon': total_sebelum_diskon,
        'total_diskon': total_diskon,
        'total_setelah_diskon': total_sebelum_diskon - total_diskon,
        'alamat_default': pelanggan.alamat,
        'transaksi': transaksi
    }
    return render(request, 'payment_form.html', context)

@login_required_pelanggan
def daftar_pesanan(request):
    pelanggan = get_object_or_404(Pelanggan, pk=request.session['pelanggan_id'])
    pesanan = Transaksi.objects.filter(idPelanggan=pelanggan).order_by('-tanggal')
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan.id)
    
    context = {
        'pesanan': pesanan,
        'notifikasi_count': notifikasi_count
    }
    return render(request, 'daftar_pesanan.html', context)

@login_required_pelanggan
def detail_pesanan(request, pesanan_id):
    pelanggan = get_object_or_404(Pelanggan, pk=request.session['pelanggan_id'])
    transaksi = get_object_or_404(Transaksi, pk=pesanan_id, idPelanggan=pelanggan)
    detail_transaksi = DetailTransaksi.objects.filter(idTransaksi=transaksi)
    
    # Calculate total including shipping cost
    total_dengan_ongkir = Decimal(str(transaksi.total)) + Decimal(str(transaksi.ongkir))
    
    # Handle feedback submission
    if request.method == 'POST' and 'submit_feedback' in request.POST:
        # Only allow feedback submission when transaction status is 'SELESAI'
        if transaksi.status_transaksi == 'SELESAI':
            feedback_text = request.POST.get('feedback', '')
            feedback_image = request.FILES.get('fotofeedback', None)
            
            # Update transaction with feedback
            transaksi.feedback = feedback_text
            if feedback_image:
                transaksi.fotofeedback = feedback_image
            transaksi.save()
            
            messages.success(request, 'Terima kasih atas feedback Anda.')
        else:
            messages.error(request, 'Feedback hanya dapat dikirim untuk transaksi yang sudah selesai.')
        
        return redirect('detail_pesanan', pesanan_id=pesanan_id)
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan.id)
    
    context = {
        'transaksi': transaksi,
        'detail_transaksi': detail_transaksi,
        'total_dengan_ongkir': total_dengan_ongkir,
        'notifikasi_count': notifikasi_count
    }
    return render(request, 'detail_pesanan.html', context)

@login_required_pelanggan
def notifikasi(request):
    pelanggan = get_object_or_404(Pelanggan, pk=request.session['pelanggan_id'])
    notifikasi_list = Notifikasi.objects.filter(idPelanggan=pelanggan).order_by('-created_at')
    
    # Logika untuk menandai notifikasi sebagai sudah dibaca
    Notifikasi.objects.filter(idPelanggan=pelanggan, is_read=False).update(is_read=True)
    
    # Get notification count (will be 0 after marking as read)
    notifikasi_count = 0
    
    context = {
        'notifikasi_list': notifikasi_list,
        'notifikasi_count': notifikasi_count
    }
    return render(request, 'notifikasi.html', context)

@login_required_pelanggan
def akun(request):
    pelanggan = get_object_or_404(Pelanggan, pk=request.session['pelanggan_id'])
    
    # Get notification count
    notifikasi_count = get_notification_count(pelanggan.id)
    
    # Calculate total purchase history
    total_belanja = Transaksi.objects.filter(
        idPelanggan=pelanggan,
        status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    if request.method == 'POST':
        form = PelangganEditForm(request.POST, instance=pelanggan)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Data akun berhasil diperbarui.')
                return redirect('akun')
            except Exception as e:
                messages.error(request, 'Terjadi kesalahan saat memperbarui data akun. Silakan coba lagi.')
        else:
            # Handle form errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PelangganEditForm(instance=pelanggan)
    
    context = {
        'pelanggan': pelanggan,
        'form': form,
        'notifikasi_count': notifikasi_count,
        'total_belanja': total_belanja
    }
    return render(request, 'akun.html', context)

# Helper function to create notifications
def create_notification(pelanggan, tipe_pesan, isi_pesan, url_target='#'):
    """
    Create a notification for a specific customer with optional CTA URL
    """
    try:
        # Use Celery task instead of direct database creation
        from .tasks import send_notification_task
        send_notification_task.delay(
            pelanggan_id=pelanggan.id,
            tipe_pesan=tipe_pesan,
            isi_pesan=isi_pesan,
            url_target=url_target
        )
        return True
    except Exception as e:
        # Log the error if needed
        return False

# Helper function to create notifications for all customers
def create_notification_for_all_customers(tipe_pesan, isi_pesan, url_target='#'):
    """
    Create a notification for all customers with optional CTA URL
    """
    try:
        from .tasks import send_notification_task
        pelanggan_list = Pelanggan.objects.all()
        for pelanggan in pelanggan_list:
            # Add CTA URL to the message if provided
            pesan = isi_pesan
            if url_target and url_target != '#':
                pesan = f"{isi_pesan} <a href='{url_target}' class='alert-link'>Lihat detail</a>"
            
            send_notification_task.delay(
                pelanggan_id=pelanggan.id,
                tipe_pesan=tipe_pesan,
                isi_pesan=pesan,
                url_target=url_target
            )
        return True
    except Exception as e:
        # Log the error if needed
        return False

# Add this helper function to get notification count
def get_notification_count(pelanggan_id):
    """
    Get the count of unread notifications for a customer
    """
    try:
        return Notifikasi.objects.filter(
            idPelanggan_id=pelanggan_id,
            is_read=False
        ).count()
    except Exception:
        return 0

# Add this helper function to get cart item count
def get_cart_item_count(request):
    """
    Get the count of items in the cart
    """
    try:
        keranjang = request.session.get('keranjang', {})
        return sum(keranjang.values())
    except Exception:
        return 0

def check_expired_payments():
    """
    Function to check for expired payments and update their status
    This should be called periodically or before processing payments
    """
    from django.utils import timezone
    from .models import Transaksi
    
    # Get all transactions with status 'DIPROSES' that have expired
    expired_transactions = Transaksi.objects.filter(
        status_transaksi='DIPROSES',
        batas_waktu_bayar__lt=timezone.now()
    )
    
    # Update their status to 'DIBATALKAN'
    for transaction in expired_transactions:
        transaction.status_transaksi = 'DIBATALKAN'
        transaction.save()
        
        # Create notification for the customer
        create_notification(
            transaction.idPelanggan,
            "Pesanan Dibatalkan",
            f"Pesanan #{transaction.id} telah dibatalkan karena melewati batas waktu pembayaran."
        )

def send_birthday_email(customer, total_spending):
    """
    Simulate sending birthday email notification
    In a real implementation, this would use Django's send_mail function
    """
    # This is a simulation - in real implementation you would use:
    # from django.core.mail import send_mail
    # send_mail(
    #     subject='Selamat Ulang Tahun! Diskon Spesial untuk Anda',
    #     message=f'Selamat ulang tahun {customer.nama_pelanggan}! Nikmati diskon 10% untuk pembelanjaan hari ini.',
    #     from_email='noreply@barokahjayabeton.com',
    #     recipient_list=[customer.email],
    #     fail_silently=False,
    # )
    
    print(f'EMAIL SIMULATION: Birthday email would be sent to {customer.email or customer.nama_pelanggan}')
    return True


def send_notification_email(subject, template_name, context, recipient_list, url_target='#'):
    """
    Send email notification using HTML template with optional CTA URL
    """
    try:
        # Add CTA URL to context if provided
        if url_target and url_target != '#':
            context['cta_url'] = url_target
        
        # Render HTML content
        html_message = render_to_string(template_name, context)
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

    # NOTE: `dashboard_analitik` view removed — analytics dashboard removed from sidebar/menu.

# Import statements for the new view
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.export import TableExport
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from io import BytesIO
from .tables import TransaksiTable
from .filters import TransaksiFilter
from .models import Transaksi

def laporan_transaksi(request):
    """
    View to generate transaction report with filtering and table features
    """
    # Initialize the filter with request data and all transactions queryset
    filter = TransaksiFilter(request.GET, queryset=Transaksi.objects.all())
    
    # Initialize the table with the filtered queryset
    table = TransaksiTable(filter.qs)
    
    # Configure the table with request for sorting and pagination
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    
    # Check if this is a PDF export request
    if request.GET.get('_pdf') == 'true':
        # Create a PDF buffer
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add title
        title = Paragraph("Laporan Transaksi - Barokah Jaya Beton", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Prepare data for the table
        table_data = [['No', 'Tanggal', 'Nama Pelanggan', 'Detail Produk', 'Total Harga']]
        
        # Get all data without pagination for PDF
        all_data = filter.qs
        
        # Definisikan daftar status yang dianggap sebagai pendapatan
        PAID_STATUSES = ['DIBAYAR', 'DIKIRIM', 'SELESAI']
        
        # Hitung Total Pendapatan hanya untuk transaksi dengan status pembayaran yang berhasil
        total_pendapatan = 0
        paid_transactions = all_data.filter(status_transaksi__in=PAID_STATUSES)
        
        for transaksi in paid_transactions:
            # Akses field 'total' di model Transaksi (Sudah Sesuai)
            total_pendapatan += transaksi.total if transaksi.total else 0
        
        for index, transaksi in enumerate(all_data, 1):
            # Format tanggal tanpa waktu
            tanggal_formatted = transaksi.tanggal.strftime('%d/%m/%Y') if transaksi.tanggal else ''
            
            # Dapatkan detail produk
            detail_produk_list = []
            
            # Akses relasi balik 'detailtransaksi_set' (Sudah Sesuai)
            detail_transaksi_set = transaksi.detailtransaksi_set.all()
            for detail in detail_transaksi_set:
                # Akses idProduk (Foreign Key ke Produk) dan nama_produk (Sudah Sesuai)
                produk_nama = detail.idProduk.nama_produk if detail.idProduk else 'N/A'
                detail_produk_list.append(f"{produk_nama} (x{detail.jumlah_produk})")
            
            detail_produk_str = '\n'.join(detail_produk_list) if detail_produk_list else '-'
            
            # Akses idPelanggan (Foreign Key ke Pelanggan) dan nama_pelanggan (Sudah Sesuai)
            pelanggan_nama = transaksi.idPelanggan.nama_pelanggan if transaksi.idPelanggan else ''
            
            table_data.append([
                str(index),
                tanggal_formatted,
                str(pelanggan_nama),
                detail_produk_str,
                f"Rp {transaksi.total:,.0f}" if transaksi.total else "Rp 0"
            ])
        
        # Create the table
        pdf_table = Table(table_data)
        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to top for multi-line content
        ]))
        
        elements.append(pdf_table)
        
        # Add total pendapatan
        elements.append(Spacer(1, 0.2*inch))
        total_pendapatan_para = Paragraph(f"<b>Total Pendapatan Keseluruhan: Rp {total_pendapatan:,.0f}</b>", styles['Normal'])
        elements.append(total_pendapatan_para)
        
        # Build the PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf_value = buffer.getvalue()
        buffer.close()
        
        # Create the HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="laporan_transaksi.pdf"'
        response.write(pdf_value)
        
        return response
    
    context = {
        'filter': filter,
        'table': table
    }
    
    return render(request, 'admin_dashboard/laporan_transaksi.html', context)

# Import statements for the best selling products report
from django.db.models import Sum, Q
from .tables import ProdukTerlarisTable
from .filters import ProdukTerlarisFilter
from .models import DetailTransaksi

def laporan_produk_terlaris(request):
    """
    View untuk menghasilkan laporan produk terlaris dengan fitur filtering dan tabel.
    Laporan hanya mencakup transaksi dengan status pembayaran yang berhasil.
    """
    
    # Inisialisasi filter dengan data request dan queryset semua produk
    # ASUMSI: ProdukTerlarisFilter diimpor dan didefinisikan dengan benar.
    filter = ProdukTerlarisFilter(request.GET, queryset=Produk.objects.all())
    
    # Dapatkan queryset produk yang sudah difilter oleh filter form
    filtered_produk = filter.qs
    
    # Ambil nilai filter tanggal dari request
    tanggal_gte = request.GET.get('tanggal_transaksi__gte')
    tanggal_lte = request.GET.get('tanggal_transaksi__lte')
    
    produk_queryset = filtered_produk
    
    # --- Pembangunan Query ORM untuk Agregasi ---
    
    # 1. Definisikan basis filter untuk transaksi yang berhasil (DIBAYAR, DIKIRIM, SELESAI)
    detail_transaksi_filter = Q(detailtransaksi__idTransaksi__status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI'])
    # CATATAN: Menggunakan idTransaksi untuk mengakses relasi dari DetailTransaksi ke Transaksi

    # 2. Tambahkan filter tanggal ke dalam Q object
    if tanggal_gte:
        detail_transaksi_filter &= Q(detailtransaksi__idTransaksi__tanggal__gte=tanggal_gte)
    
    if tanggal_lte:
        # Gunakan Q(tanggal__date__lte=tanggal_lte) jika field 'tanggal' di Transaksi adalah DateTimeField
        detail_transaksi_filter &= Q(detailtransaksi__idTransaksi__tanggal__date__lte=tanggal_lte)
    
    # 3. Anotasi (Annotate) queryset produk dengan data agregasi
    produk_queryset = produk_queryset.annotate(
        # Menghitung total kuantitas terjual (jumlah_produk)
        total_kuantitas_terjual=Sum(
            'detailtransaksi__jumlah_produk',
            filter=detail_transaksi_filter
        ),
        # Menghitung total pendapatan (sub_total)
        total_pendapatan=Sum(
            'detailtransaksi__sub_total',
            filter=detail_transaksi_filter
        )
    ).filter(
        # Hanya tampilkan produk yang terjual minimal 1 unit
        total_kuantitas_terjual__gt=0
    ).order_by(
        # Urutkan berdasarkan kuantitas terjual tertinggi
        '-total_kuantitas_terjual'
    )
    
    # --- Setup Tabel HTML ---
    
    # Inisialisasi tabel dengan queryset yang sudah di-annotate
    # ASUMSI: ProdukTerlarisTable diimpor dan didefinisikan dengan benar.
    table = ProdukTerlarisTable(produk_queryset)
    
    # Konfigurasi tabel untuk sorting dan pagination
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    
    # --- Generate PDF Export ---
    
    if request.GET.get('_pdf') == 'true':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1 
        )
        
        # Add title
        title = Paragraph("Laporan Produk Terlaris - Barokah Jaya Beton", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Prepare data for the table
        table_data = [['No', 'Nama Produk', 'Total Kuantitas Terjual', 'Total Pendapatan']]
        
        # Dapatkan semua data (queryset yang sudah terfilter dan terurut)
        all_data = produk_queryset
        total_pendapatan_keseluruhan = 0
        
        for index, produk in enumerate(all_data, 1):
            # Ambil nilai total pendapatan yang sudah di-annotate
            pendapatan = produk.total_pendapatan if produk.total_pendapatan is not None else 0
            total_pendapatan_keseluruhan += pendapatan
            
            table_data.append([
                str(index),
                str(produk.nama_produk),
                str(produk.total_kuantitas_terjual or 0),
                f"Rp {pendapatan:,.0f}"
            ])
        
        # Create the table
        pdf_table = Table(table_data)
        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Rata kiri/kanan untuk data numerik
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'), # Kolom Kuantitas & Pendapatan Rata Kanan
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),   # Kolom Nama Produk Rata Kiri
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9), # Ukuran Font diperkecil sedikit agar muat
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(pdf_table)
        
        # Add total pendapatan keseluruhan
        elements.append(Spacer(1, 0.2*inch))
        total_pendapatan_para = Paragraph(f"<b>Total Pendapatan Keseluruhan: Rp {total_pendapatan_keseluruhan:,.0f}</b>", styles['Normal'])
        elements.append(total_pendapatan_para)
        
        # Build the PDF
        doc.build(elements)
        
        pdf_value = buffer.getvalue()
        buffer.close()
        
        # Create the HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="laporan_produk_terlaris.pdf"'
        response.write(pdf_value)
        
        return response
    
    # --- Render Halaman HTML ---
    
    context = {
        'filter': filter,
        'table': table
    }
    
    return render(request, 'admin_dashboard/laporan_produk_terlaris.html', context)


def custom_admin_index(request):
    """
    Custom admin dashboard view that provides data analytics for the admin panel:
    - Monthly Revenue (last 6 months)
    - Top 5 Best Selling Products
    - Top 3 Loyal Customers
    
    This function only returns data, not a response, to avoid recursion errors.
    """
    from django.db.models import Sum, Avg, Count, Max, Min
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate monthly revenue for the last 6 months
    today = timezone.now()
    monthly_revenue = []
    
    # Define status that count as completed transactions
    COMPLETED_STATUSES = ['SELESAI']
    
    for i in range(5, -1, -1):  # Last 6 months (including current)
        start_date = (today - timedelta(days=30*i)).replace(day=1)
        if i == 0:  # Current month
            end_date = today
        else:
            # Last day of the month
            next_month = (today - timedelta(days=30*(i-1))).replace(day=1)
            end_date = next_month - timedelta(days=1)
            
        monthly_total = Transaksi.objects.filter(
            status_transaksi__in=COMPLETED_STATUSES,
            tanggal__gte=start_date,
            tanggal__lte=end_date
        ).aggregate(total=Sum('total'))['total'] or 0
        
        monthly_revenue.append({
            'month': start_date.strftime('%B %Y'),
            'total': float(monthly_total)
        })
    
    # Get top 5 best selling products (by quantity)
    top_products = DetailTransaksi.objects.filter(
        idTransaksi__status_transaksi__in=COMPLETED_STATUSES
    ).values(
        'idProduk__nama_produk'
    ).annotate(
        kuantitas_terjual=Sum('jumlah_produk'),
        total_pendapatan=Sum('sub_total')
    ).order_by('-kuantitas_terjual')[:5]
    
    # Get top 3 loyal customers (by total purchase amount)
    top_customers = Transaksi.objects.filter(
        status_transaksi__in=COMPLETED_STATUSES
    ).values(
        'idPelanggan__nama_pelanggan'
    ).annotate(
        total_transaksi=Sum('total')
    ).order_by('-total_transaksi')[:3]
    
    # Return only the analytics data
    return {
        'monthly_revenue': monthly_revenue,
        'top_products': top_products,
        'top_customers': top_customers
    }

