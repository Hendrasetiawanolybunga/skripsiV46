# LAPORAN ANALISIS LENGKAP PROYEK: BAROKAH JAYA BETON

**Tanggal Laporan:** 28 November 2025  
**Nama Proyek:** ProyekBarokah - Sistem E-Commerce & Admin Management  
**Framework:** Django 4.2, WebSocket (Daphne), Celery Task Queue  
**Database:** SQLite3

---

## 📋 DAFTAR ISI

1. [Ringkasan Eksekutif](#ringkasan-eksekutif)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Models & Database Schema](#models--database-schema)
4. [User Personas & Alur Bisnis](#user-personas--alur-bisnis)
5. [Fitur Utama & Implementasi](#fitur-utama--implementasi)
6. [Admin Dashboard](#admin-dashboard)
7. [Karyawan Interface](#karyawan-interface)
8. [Template & UI/UX](#template--uiux)
9. [Logic Bisnis Utama](#logic-bisnis-utama)
10. [Teknologi & Dependencies](#teknologi--dependencies)
11. [Security & Validasi](#security--validasi)
12. [Potential Issues & Rekomendasi](#potential-issues--rekomendasi)

---

## 📊 RINGKASAN EKSEKUTIF

Proyek **Barokah Jaya Beton** adalah sistem e-commerce terintegrasi dengan 3 role utama:
- **Pelanggan (Customer)**: Membeli produk, manage keranjang, tracking pesanan
- **Admin**: Mengelola inventori, diskon, laporan, verifikasi pembayaran
- **Karyawan**: Verifikasi pengiriman fisik & update status pesanan

**Fitur Utama:**
✅ Registrasi & Login Pelanggan (session-based)  
✅ Keranjang Belanja dengan Stock Management  
✅ Sistem Diskon Multi-Tier (Birthday, Loyalty, Manual)  
✅ Notifikasi Real-time (WebSocket + Celery)  
✅ Admin Dashboard dengan Analytics  
✅ Tracking Pesanan & Feedback System  
✅ Verifikasi Pengiriman oleh Karyawan  

---

## 🏗️ ARSITEKTUR SISTEM

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Customer)                   │
│  - Beranda, Product List, Cart, Checkout, Order Track  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────────────────────┐
│         DJANGO APPLICATION (ProyekBarokah)              │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Views Layer (admin_dashboard)            │   │
│  │  - Auth (Register, Login, Logout)               │   │
│  │  - Shopping (Cart, Checkout, Payment)           │   │
│  │  - Tracking (Order List, Order Detail)          │   │
│  │  - Account Management                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │      Business Logic & Service Layer              │   │
│  │  - Discount Calculation (P1, P2-A, P2-B)        │   │
│  │  - Stock Management                             │   │
│  │  - Notification Handler                         │   │
│  │  - Payment Processing                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │       Models Layer (Database ORM)                │   │
│  │  - Pelanggan, Produk, Transaksi, DiskonPelanggan│   │
│  │  - DetailTransaksi, Notifikasi, Karyawan       │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        │          │          │          │
┌───────▼─┐  ┌────▼───┐  ┌──▼──┐  ┌───▼────┐
│ SQLite3 │  │ Celery │  │Redis│  │ Daphne │
│Database │  │ Queue  │  │Cache│  │ WS Srv │
└─────────┘  └────────┘  └─────┘  └────────┘
```

---

## 🗄️ MODELS & DATABASE SCHEMA

### 1. **Model Pelanggan**
```python
class Pelanggan(models.Model):
    - id (PK, AutoField)
    - nama_pelanggan (CharField)
    - username (CharField, UNIQUE) → Login identifier
    - password (CharField) → Hashed with make_password()
    - email (EmailField, UNIQUE, NULLABLE)
    - alamat (TextField)
    - tanggal_lahir (DateField) → Untuk birthday discount
    - no_hp (CharField)
```

**Relasi:**
- 1 Pelanggan → Many Transaksi (OneToMany)
- 1 Pelanggan → Many DiskonPelanggan (OneToMany)
- 1 Pelanggan → Many Notifikasi (OneToMany)

---

### 2. **Model Produk & Kategori**
```python
class Kategori(models.Model):
    - id (PK, AutoField)
    - nama_kategori (CharField)

class Produk(models.Model):
    - id (PK, AutoField)
    - nama_produk (CharField)
    - deskripsi_produk (TextField)
    - foto_produk (ImageField) → /media/produk_images/
    - stok_produk (IntegerField)
    - harga_produk (DecimalField, max_digits=10, decimal_places=2)
    - kategori (ForeignKey to Kategori)
```

---

### 3. **Model Transaksi & DetailTransaksi**
```python
class Transaksi(models.Model):
    - id (PK, AutoField)
    - idPelanggan (FK to Pelanggan)
    - tanggal (DateTimeField, default=timezone.now)
    - total (DecimalField) → Total harga setelah diskon + ongkir
    - ongkir (DecimalField, default=0)
    - status_transaksi (CharField) → DIPROSES, DIBAYAR, DIKIRIM, SELESAI, DIBATALKAN
    - bukti_bayar (FileField, NULLABLE) → /media/bukti_pembayaran/
    - alamat_pengiriman (TextField, NULLABLE)
    - feedback (TextField, NULLABLE) → Customer feedback
    - fotofeedback (ImageField, NULLABLE) → /media/feedback_images/
    - waktu_checkout (DateTimeField, NULLABLE)
    - batas_waktu_bayar (DateTimeField, NULLABLE) → 24 jam dari checkout
    - foto_pengiriman (ImageField, NULLABLE) → /media/verifikasi_pengiriman/

class DetailTransaksi(models.Model):
    - id (PK, AutoField)
    - idTransaksi (FK to Transaksi)
    - idProduk (FK to Produk)
    - jumlah_produk (IntegerField)
    - sub_total (DecimalField) → After discount
```

---

### 4. **Model DiskonPelanggan (Multi-tier Discount)**
```python
class DiskonPelanggan(models.Model):
    - id (PK, AutoField)
    - idPelanggan (FK to Pelanggan)
    - idProduk (FK to Produk, NULLABLE) → If NULL = general discount
    - persen_diskon (IntegerField) → Percentage (e.g., 10)
    - status (CharField) → 'aktif' or 'tidak_aktif'
    - pesan (TextField, NULLABLE)
    - tanggal_dibuat (DateTimeField, auto_now_add=True)
    - berlaku_sampai (DateTimeField, NULLABLE)
    - scope_diskon (CharField) → SINGLE_PRODUCT, ALL_PRODUCTS, CART_THRESHOLD
    - minimum_cart_total (DecimalField, NULLABLE) → For CART_THRESHOLD scope
```

**Scope Types:**
- `SINGLE_PRODUCT`: Diskon untuk produk tertentu saja
- `ALL_PRODUCTS`: Diskon untuk semua produk (P2-A: Loyalitas Permanen)
- `CART_THRESHOLD`: Diskon jika total cart mencapai minimum (P2-B: Loyalitas Instan)

---

### 5. **Model Notifikasi**
```python
class Notifikasi(models.Model):
    - id (PK, AutoField)
    - idPelanggan (FK to Pelanggan)
    - tipe_pesan (CharField) → Notification type
    - isi_pesan (TextField) → HTML content with CTA
    - is_read (BooleanField, default=False)
    - created_at (DateTimeField, auto_now_add=True)
    - link_cta (CharField, NULLABLE) → Call-to-action URL
```

---

### 6. **Model Karyawan**
```python
class Karyawan(models.Model):
    - id (PK, AutoField)
    - nama (CharField)
    - email (EmailField, UNIQUE)
    - password (CharField) → Hashed with make_password()
    - is_active (BooleanField, default=True)
    - created_at (DateTimeField, auto_now_add=True)
    
    Methods:
    - set_password(raw_password) → Hash password
    - check_password(raw_password) → Verify password
```

---

### 7. **Model Admin**
```python
class Admin(AbstractUser):
    - Inherits from Django's AbstractUser
    - nama_lengkap (CharField) → Full name
    - Uses default fields: username, password, email, is_staff, is_superuser
```

---

## 👥 USER PERSONAS & ALUR BISNIS

### 📍 ALUR 1: REGISTRASI PELANGGAN

```
START
  ↓
[1] Customer membuka halaman register (/register/)
  ↓
[2] Customer mengisi form:
    - Username (UNIQUE)
    - Nama Lengkap
    - Email (UNIQUE, format validation)
    - Alamat
    - Tanggal Lahir
    - No HP
    - Password & Konfirmasi
  ↓
[3] Sistem validasi form:
    - Check password match
    - Check email format
    - Check unique username & email
  ↓
[4] Data disimpan ke database:
    - Password di-hash dengan make_password()
    - Pelanggan record dibuat
  ↓
[5] Check apakah hari ini birthday:
    IF tanggal_lahir == hari ini THEN
        Buat notifikasi: "Selamat Ulang Tahun!"
        Diskon 10% otomatis teraplikasi untuk checkout hari ini
    END IF
  ↓
[6] Success message: "Akun berhasil dibuat. Silakan login."
  ↓
REDIRECT ke login page
END
```

---

### 📍 ALUR 2: LOGIN & DASHBOARD PELANGGAN

```
START
  ↓
[1] Customer membuka halaman login (/login/)
  ↓
[2] Customer input username & password
  ↓
[3] Sistem verifikasi:
    - Query Pelanggan dengan username
    - Verify password dengan check_password()
  ↓
[4] IF password valid THEN
    - Set session['pelanggan_id'] = pelanggan.id
    - Save session
    ELSE
    - Show error: "Username atau password salah"
    END IF
  ↓
[5] IF login valid THEN
    - REDIRECT ke dashboard_pelanggan
    - Display: Nama customer, 3 produk terbaru, notifikasi count
    ELSE
    - STAY on login page
    END IF
  ↓
END
```

---

### 📍 ALUR 3: BELANJA (ADD TO CART → CHECKOUT → PAYMENT)

```
START: Customer melihat produk list
  ↓
[1] Customer klik "Tambah ke Keranjang" di product detail
  ↓
[2] Input jumlah produk & klik "Tambah"
  ↓
[3] Sistem validasi stok:
    IF (current_quantity_in_cart + new_quantity) > stok_produk THEN
        Adjust jumlah ke stok tersedia
        Show warning message
    ELSE
        Add ke keranjang
    END IF
  ↓
[4] Check birthday & send notification:
    IF tanggal_lahir == hari ini THEN
        Check loyalty status:
        - Jika loyal (total transaksi DIBAYAR/DIKIRIM/SELESAI >= Rp 5jt):
            Send: "Diskon Ulang Tahun Permanen 10% untuk 3 produk favorit"
        - Jika tidak loyal:
            Send: "Diskon Ulang Tahun Instan 10% jika cart >= Rp 5jt"
    END IF
  ↓
[5] Customer REDIRECT ke keranjang (/keranjang/)
  ↓
[6] Di Keranjang:
    - Display: Produk, harga, diskon (jika ada), sub_total
    - Calculate total dengan semua diskon
    - Display: Total sebelum diskon, potongan harga, total akhir
    - Show status loyalitas & eligibility diskon
  ↓
[7] Customer klik "Checkout"
  ↓
[8] Store cart ke session['checkout_data']
  ↓
[9] REDIRECT ke proses_pembayaran
  ↓
[10] Di Payment Page:
     - Display cart items & total
     - Form: Bukti Pembayaran (file upload)
     - Form: Alamat Pengiriman (optional, default = alamat di profile)
  ↓
[11] Customer submit form
  ↓
[12] Sistem proses pembayaran:
     - Validate bukti_bayar file
     - Create Transaksi record:
       * Set waktu_checkout = NOW()
       * Set batas_waktu_bayar = NOW() + 24 hours
       * status = 'DIPROSES'
       * Total = 0 (akan di-calculate)
  ↓
[13] Process setiap item di keranjang:
     FOR EACH item:
         - Check stok final
         - Check diskon applicable:
           * Priority 1: Manual discount (idProduk specific)
           * Priority 2: General discount (idProduk NULL)
           * Priority 3: Birthday discount
             - P2-A (Loyal + Birthday): Terapkan 10% ke 3 produk favorit
             - P2-B (Non-Loyal + Birthday + Cart >= 5jt): Terapkan 10% ke total cart
         - Calculate: sub_total = (harga - diskon) * jumlah
         - Reduce stok produk
         - Create DetailTransaksi record
         - Add ke total_belanja
     END FOR
  ↓
[14] Update Transaksi.total = total_belanja
  ↓
[15] Clear session['keranjang'] & session['checkout_data']
  ↓
[16] Create notification: "Pesanan #{id} berhasil dibuat"
  ↓
[17] Success message & REDIRECT ke daftar_pesanan
  ↓
END
```

---

### 📍 ALUR 4: ADMIN VERIFIKASI PEMBAYARAN

```
START: Admin login ke Django Admin (Jazzmin)
  ↓
[1] Admin buka Transaksi list (filter: status_transaksi='DIPROSES')
  ↓
[2] Admin review bukti_bayar
  ↓
[3] Admin klik "Change" untuk edit transaksi
  ↓
[4] Admin ubah status_transaksi ke 'DIBAYAR'
  ↓
[5] Sistem trigger:
    - Create notification: "Pembayaran Anda telah dikonfirmasi"
    - Status berubah ke DIBAYAR
    - Karyawan bisa mulai proses pengiriman
  ↓
[6] Save & REDIRECT ke transaksi list
  ↓
END
```

---

### 📍 ALUR 5: ADMIN MANAGE DISKON

```
START: Admin login
  ↓
[1] Admin buka Admin Dashboard (Diskon Pelanggan section)
  ↓
[2] Admin bisa:
    a) Create diskon baru:
       - Select Pelanggan & (optional) Produk
       - Input persen_diskon
       - Select scope_diskon (SINGLE_PRODUCT / ALL_PRODUCTS / CART_THRESHOLD)
       - If CART_THRESHOLD: input minimum_cart_total
       - Set berlaku_sampai (expiry date)
       - Save
    
    b) Edit diskon existing:
       - Modify persen_diskon, status, berlaku_sampai
       - Save
    
    c) Delete diskon:
       - Confirm & delete
  ↓
[3] Admin action: "Set Birthday Discount for Loyal Customers"
    - Filter customers dengan birthday HARI INI
    - Check loyalty status (total >= 5jt)
    - Create/update DiskonPelanggan untuk 3 produk favorit (P2-A)
    - Send notification ke customer
    - Send email (jika email ada)
  ↓
[4] Save & show success message
  ↓
END
```

---

### 📍 ALUR 6: KARYAWAN VERIFIKASI PENGIRIMAN

```
START: Karyawan login (/karyawan/login/)
  ↓
[1] Karyawan input email & password
  ↓
[2] Sistem verifikasi:
    - Query Karyawan dengan email
    - Check password
    - Check is_active
  ↓
[3] IF valid THEN
    - Set session['karyawan_id']
    - REDIRECT ke karyawan_dashboard
    ELSE
    - Show error message
    END IF
  ↓
[4] Di Karyawan Dashboard:
    - Display list transaksi dengan status='DIKIRIM'
    - Each row: Customer name, order #, total, alamat, action button
  ↓
[5] Karyawan klik tombol "Verifikasi Pengiriman"
  ↓
[6] Di Verification Page:
    - Display order details
    - Form:
      * Upload foto_pengiriman (proof of delivery)
      * Select status_transaksi dropdown
  ↓
[7] Karyawan upload foto & ubah status ke 'SELESAI'
  ↓
[8] Sistem validasi:
    - Foto harus ada jika status = SELESAI
  ↓
[9] Save & REDIRECT ke dashboard
  ↓
[10] Transaksi status updated to SELESAI
    - Notification: "Pesanan Anda telah selesai"
    - Customer bisa submit feedback
  ↓
END
```

---

### 📍 ALUR 7: ADMIN DASHBOARD ANALITIK

```
START: Admin login
  ↓
[1] Admin buka custom admin dashboard (/admin/)
  ↓
[2] Dashboard display:
    a) Monthly Revenue Chart (6 bulan terakhir)
       - Filter: status_transaksi IN ['DIBAYAR', 'DIKIRIM', 'SELESAI']
       - Calculate: Sum(total) per bulan
    
    b) Latest Transactions Table
       - Show: 5 transaksi terbaru
       - Include: Customer, total, status, date
    
    c) Low Stock Products Table
       - Show: Produk dengan stok < 10
       - Sort by: stok_produk ASC
  ↓
[3] Admin bisa review data real-time
  ↓
END
```

---

## ⚙️ FITUR UTAMA & IMPLEMENTASI

### 1. **Sistem Diskon Multi-Tier (P1, P2-A, P2-B)**

#### **P1: Manual Product-Specific Discount**
- Admin set diskon untuk produk tertentu ke customer tertentu
- Scope: `SINGLE_PRODUCT`
- Contoh: Diskon 5% untuk produk "Semen" ke pelanggan "Budi"
- Priority: **HIGHEST**

#### **P2-A: Birthday + Loyalty (Permanent Discount)**
- Trigger: Pelanggan punya ulang tahun HARI INI AND total transaksi >= Rp 5jt
- Diskon: 10% untuk 3 produk favorit mereka
- Scope: `ALL_PRODUCTS` (tapi hanya ke 3 produk favorit)
- Duration: 24 jam (atau sampai ekspirasi)
- Notifikasi: "Diskon Ulang Tahun Permanen 10% untuk 3 produk favorit Anda"
- Priority: **MEDIUM**

#### **P2-B: Birthday + Instant Loyalty (Instant Discount)**
- Trigger: Pelanggan punya ulang tahun HARI INI AND total cart >= Rp 5jt (meskipun belum pernah loyal)
- Diskon: 10% untuk SEMUA item di cart
- Scope: `CART_THRESHOLD`
- Minimum threshold: Rp 5jt
- Applied: Di checkout/payment, ke total cart
- Notifikasi: "Diskon Ulang Tahun Instan 10% untuk belanja hari ini jika cart >= Rp 5jt"
- Priority: **LOW** (hanya jika tidak ada diskon P1 atau P2-A)

**Discount Priority Logic (dalam checkout):**
```python
IF manual_discount_single_product THEN
    Apply manual_discount (highest priority)
ELSE IF manual_discount_general THEN
    Apply manual_discount
ELSE IF birthday_and_loyal THEN
    Apply P2-A (10% to top 3 products)
ELSE IF birthday_and_cart_threshold THEN
    Apply P2-B (10% to total cart)
ELSE
    No discount
END IF
```

---

### 2. **Stock Management**

**Validation Points:**
1. **Add to Cart**: Check jika `current_quantity_in_cart + new_quantity <= stok_produk`
2. **Checkout**: Final validation sebelum create DetailTransaksi
3. **Payment Processing**: Stock dikurangi saat transaksi di-process (atomic transaction)

**Stock Update Logic:**
```python
WITH transaction.atomic():
    FOR EACH item IN cart:
        IF stok_produk < quantity_requested THEN
            Adjust to available stock OR remove item
        ELSE
            produk.stok_produk -= quantity_requested
            produk.save()
            Create DetailTransaksi
        END IF
    END FOR
    Commit semua changes
END WITH
```

---

### 3. **Session-based Authentication**

**Pelanggan:**
- `request.session['pelanggan_id']` = Pelanggan.id
- Decorator: `@login_required_pelanggan`
- Logout: Clear session['pelanggan_id']

**Karyawan:**
- `request.session['karyawan_id']` = Karyawan.id
- Decorator: `@karyawan_required`
- Logout: Clear session['karyawan_id']

**Admin:**
- Uses Django's built-in auth system
- Decorator: `@login_required` + check `is_staff`

---

### 4. **Real-time Notifications (WebSocket + Celery)**

**Stack:**
- **Daphne**: ASGI server untuk WebSocket
- **Channels**: Django WebSocket integration
- **Celery**: Background task queue
- **Redis**: Message broker (optional)

**Flow:**
```
1. Admin approve payment → Trigger celery task
2. Task create_notification() dalam database
3. Task send via channel_layer (WebSocket)
4. Customer terima notifikasi real-time
```

**Task: `send_notification_task`**
```python
@shared_task
def send_notification_task(pelanggan_id, tipe_pesan, isi_pesan, url_target):
    - Create Notifikasi in database
    - Send via WebSocket group: f"user_{pelanggan_id}"
    - Include: id, tipe_pesan, isi_pesan, created_at
```

---

### 5. **Payment & Order Lifecycle**

**Status Flow:**
```
DIPROSES → DIBAYAR → DIKIRIM → SELESAI
   ↓          ↓
   └─ DIBATALKAN (jika expired atau reject)
```

**Validations:**
- Payment deadline: 24 jam dari `waktu_checkout`
- Karyawan hanya bisa verifikasi transaksi status DIKIRIM
- Customer hanya bisa submit feedback untuk transaksi SELESAI

---

## 📊 ADMIN DASHBOARD

### **Fitur:**

1. **Custom Admin Index** (`/admin/`)
   - Override default Django admin dashboard
   - Menggunakan Jazzmin untuk UI improvement
   - Custom CSS & icons

2. **Laporan Pendapatan Bulanan**
   - Endpoint: `/laporan/transaksi/`
   - Chart: Bar chart 6 bulan terakhir
   - Data: Sum(total) untuk transaksi DIBAYAR/DIKIRIM/SELESAI

3. **Laporan Produk Terlaris**
   - Endpoint: `/laporan/produk-terlaris/`
   - Ranking: Top 10 produk berdasarkan quantity sold
   - Data: Produk, qty, revenue

4. **Transaksi Management**
   - View & edit transaksi
   - Bulk action: Set Birthday Discount
   - Filter: Status, date range, customer

5. **Pelanggan Management**
   - View & edit data pelanggan
   - Display: Total belanja, loyalitas status, birthday flag
   - Bulk action: Birthday discount trigger

6. **Diskon Management**
   - Create/edit/delete DiskonPelanggan
   - Set scope & expiry date
   - Bulk update status

---

## 👔 KARYAWAN INTERFACE

### **Fitur:**

1. **Login Page** (`/karyawan/login/`)
   - Email & password
   - Session-based auth

2. **Dashboard** (`/karyawan/dashboard/`)
   - List transaksi status DIKIRIM
   - Table: #Order, Customer, Total, Alamat
   - Button: "Verifikasi Pengiriman"

3. **Verification Page** (`/karyawan/transaksi/<id>/verifikasi/`)
   - Display order details
   - Form: Upload foto_pengiriman
   - Dropdown: Change status to SELESAI
   - Validation: Foto wajib saat status = SELESAI

---

## 🎨 TEMPLATE & UI/UX

### **Customer-facing Templates:**

| Page | Path | Deskripsi |
|------|------|-----------|
| Beranda | `templates/beranda_umum.html` | Landing page dengan gallery & featured products |
| Register | `templates/register.html` | Form registrasi pelanggan |
| Login | `templates/login.html` | Form login pelanggan |
| Dashboard | `templates/dashboard_pelanggan.html` | Customer dashboard (3 produk terbaru, notifikasi) |
| Product List | `templates/product_list.html` | All products dengan filter kategori & diskon badges |
| Product Detail | `templates/product_detail.html` | Detail produk, harga, diskon, add to cart button |
| Cart | `templates/keranjang.html` | Keranjang belanja dengan summary diskon & total |
| Payment | `templates/payment_form.html` | Form pembayaran (upload bukti, alamat pengiriman) |
| Order List | `templates/daftar_pesanan.html` | List semua pesanan customer |
| Order Detail | `templates/detail_pesanan.html` | Detail pesanan, feedback form, shipping status |
| Notification | `templates/notifikasi.html` | Notification center |
| Account | `templates/akun.html` | Edit profile, view total spending |

### **Admin Templates:**

| Page | Path | Deskripsi |
|------|------|-----------|
| Admin Index | `templates/admin_dashboard/admin_index_override.html` | Custom dashboard (revenue chart, latest tx, low stock) |
| Analytics | `templates/admin_dashboard/dashboard_analitik.html` | Analytics dashboard |
| Sales Report | `templates/admin_dashboard/laporan_transaksi.html` | Transaction report |
| Best Sellers | `templates/admin_dashboard/laporan_produk_terlaris.html` | Best-selling products report |

### **Karyawan Templates:**

| Page | Path | Deskripsi |
|------|------|-----------|
| Login | `templates/karyawan/login.html` | Karyawan login form |
| Dashboard | `templates/karyawan/dashboard.html` | List pesanan untuk diverifikasi |
| Verification | `templates/karyawan/verifikasi.html` | Form verifikasi pengiriman |

### **Styling:**

**Files:**
- `static/css/app.css` - Main stylesheet
- `static/css/dynamic-navbar.css` - Responsive navbar
- `static/js/app.js` - Main JavaScript

**Key Classes:**
- `.favorite-product-badge` - Yellow badge untuk produk favorit (P2-A)
- `.birthday-discount-badge` - Pink badge untuk birthday discount
- `.discount-label` - Diskon display
- `.product-image-detail` - Modal image responsive

---

## 💼 LOGIC BISNIS UTAMA

### **1. Birthday Detection & Notification**

**Trigger Points:**
1. Saat registrasi → Check tanggal_lahir == hari ini
2. Saat add to cart → Check & send notification (jika belum terkirim hari ini)
3. Celery task (`check_birthday_and_loyalty_task`) → Scheduled daily

**Logic:**
```python
# At registration
IF pelanggan.tanggal_lahir.month == TODAY.month AND 
   pelanggan.tanggal_lahir.day == TODAY.day:
    create_notification(pelanggan, "Selamat Ulang Tahun!", ...)
    
# At checkout
IF is_birthday AND is_loyal:
    # P2-A: Apply 10% to top 3 products
    diskon_produk = create_or_update_diskon_p2a()
ELSE IF is_birthday AND NOT is_loyal:
    # P2-B: Apply 10% to cart total if >= 5jt
    IF total_cart >= 5000000:
        diskon_produk = create_or_update_diskon_p2b()
```

---

### **2. Loyalty Status Calculation**

```python
def is_loyal(pelanggan):
    total_spending = Transaksi.objects.filter(
        idPelanggan=pelanggan,
        status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    return total_spending >= 5000000  # >= Rp 5jt
```

---

### **3. Top 3 Favorite Products**

```python
def get_top_purchased_products(pelanggan_id, limit=3):
    successful_tx = Transaksi.objects.filter(
        idPelanggan_id=pelanggan_id,
        status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']
    )
    
    top_products = DetailTransaksi.objects.filter(
        idTransaksi__in=successful_tx
    ).values('idProduk').annotate(
        total_qty=Sum('jumlah_produk')
    ).order_by('-total_qty')[:limit]
    
    return Produk.objects.filter(
        id__in=[item['idProduk'] for item in top_products]
    )
```

---

### **4. Discount Application in Checkout**

**Priority Order:**
1. Manual single-product discount (idProduk specific)
2. Manual general discount (idProduk NULL)
3. ALL_PRODUCTS discount (P2-A)
4. CART_THRESHOLD discount (P2-B)
5. Birthday discount (10% to favorites or total)

**Code Flow (simplified):**
```python
# Per item discount
diskon = None
IF manual_single THEN
    diskon = manual_single
ELSE IF manual_general THEN
    diskon = manual_general
ELSE IF all_products_discount THEN
    diskon = all_products_discount
ELSE IF qualifies_for_p2a AND item_id IN top_3 THEN
    diskon = mock_diskon(10%)
END IF

# Apply discount
IF diskon:
    sub_total = harga_satuan - (harga_satuan * diskon.persen / 100)
END IF

# P2-B: Applied to total cart after loop
IF qualifies_for_p2b AND cart_threshold_discount:
    total_belanja -= total_belanja * 10 / 100
END IF
```

---

### **5. Stock Deduction (Atomic Transaction)**

```python
@transaction.atomic()
try:
    FOR EACH item IN cart:
        # Validate stock
        IF produk.stok_produk < jumlah:
            ADJUST or REMOVE item
        
        # Final validation
        IF produk.stok_produk < jumlah:
            RAISE ValueError("Stok tidak cukup")
        
        # Deduct & save
        produk.stok_produk -= jumlah
        produk.save()
        
        # Create detail
        DetailTransaksi.create(...)
    END FOR
    
    # Update transaction total
    transaksi.total = total_belanja
    transaksi.save()
    
EXCEPT Exception:
    ROLLBACK all changes
    SHOW error message
```

---

## 🔧 TEKNOLOGI & DEPENDENCIES

### **Backend Stack:**

```
Django 4.2.x
- django-extensions
- django-tables2
- django-filters
- django-import-export

Celery (Task Queue)
- celery[redis]
- kombu

Channels (WebSocket)
- channels
- daphne
- channels-redis

Database & Cache
- SQLite3 (development)
- Redis (optional, for Celery broker)

Admin UI
- jazzmin (enhanced admin interface)

File Storage
- Pillow (image processing)
- whitenoise (static files)

Email
- django-anymail (optional, for production email)
```

### **Frontend:**

```
HTML5 + Bootstrap 5
- Responsive design
- Form validation

CSS3
- Custom stylesheets
- Responsive badges & modals

JavaScript (Vanilla)
- AJAX requests (XMLHttpRequest)
- Dynamic cart updates
- WebSocket connection (if implemented)
```

### **Settings Configuration:**

**Database:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Static & Media Files:**
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Celery Configuration:**
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

**Email Configuration:**
```python
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.hostanda.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'user@domain.com'
    EMAIL_HOST_PASSWORD = 'password'

DEFAULT_FROM_EMAIL = 'admin@barokah.com'
```

**Channels Configuration:**
```python
INSTALLED_APPS = [
    'daphne',
    'channels',
    ...
]

ASGI_APPLICATION = 'ProyekBarokah.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

---

## 🔐 SECURITY & VALIDASI

### **Authentication & Authorization:**

1. **Pelanggan:**
   - Session-based auth dengan `pelanggan_id`
   - Password hashed menggunakan `make_password()`
   - Verification: `check_password()`
   - Logout clears session

2. **Karyawan:**
   - Separate model dari Admin
   - Session-based auth dengan `karyawan_id`
   - `is_active` flag untuk deactivate
   - Permission-based access control

3. **Admin:**
   - Django's built-in authentication
   - `is_staff` required untuk admin access
   - `is_superuser` untuk full access

### **Input Validation:**

**Form Validation:**
- Email format check (regex pattern)
- Password confirmation match
- Username & email uniqueness
- File upload type & size check

**Business Logic Validation:**
- Stock availability check
- Payment deadline validation (24 jam)
- Transaksi status transition rules
- Feedback only for completed orders

### **Data Protection:**

1. **Password Security:**
   ```python
   # Using Django's password hashing
   user.password = make_password(raw_password)
   user.check_password(raw_password)  # Returns Boolean
   ```

2. **File Upload Security:**
   - Uploaded files stored di `/media/` (separate dari code)
   - File types restricted (image, document only)
   - Filename sanitized

3. **SQL Injection Protection:**
   - Using ORM (Django models)
   - No raw SQL queries
   - Parameterized queries via `objects.filter()`

4. **CSRF Protection:**
   - Django middleware: `CsrfViewMiddleware`
   - Form uses `{% csrf_token %}`

---

## ⚠️ POTENTIAL ISSUES & REKOMENDASI

### **Issue 1: Stock Race Condition**

**Problem:**
- Jika 2 customer simultaneously checkout item terakhir, stok bisa menjadi negatif

**Solution:**
- Implementasi `select_for_update()` untuk atomic lock:
```python
WITH transaction.atomic():
    produk = Produk.objects.select_for_update().get(pk=produk_id)
    IF produk.stok_produk >= jumlah:
        produk.stok_produk -= jumlah
        produk.save()
    ELSE:
        RAISE InsufficientStockException
```

---

### **Issue 2: Payment Status Ambiguity**

**Problem:**
- Jika admin lupa update pembayaran ke DIBAYAR, status stuck di DIPROSES

**Solution:**
- Implement payment deadline automation:
```python
@periodic_task(run_every=crontab(minute=0, hour='*'))
def check_payment_deadline():
    overdue_tx = Transaksi.objects.filter(
        status_transaksi='DIPROSES',
        batas_waktu_bayar__lt=timezone.now()
    )
    for tx in overdue_tx:
        tx.status_transaksi = 'DIBATALKAN'
        tx.save()
        create_notification(tx.idPelanggan, "Pesanan Dibatalkan", 
                          "Waktu pembayaran Anda telah habis.")
```

---

### **Issue 3: Birthday Discount Loophole**

**Problem:**
- Customer bisa exploit dengan multiple checkout pada tanggal ulang tahun

**Solution:**
- Add flag untuk track discount dipakai:
```python
class Transaksi:
    birthday_discount_applied = models.BooleanField(default=False)
    
# Check sebelum apply
IF is_birthday AND NOT tx.birthday_discount_applied:
    Apply discount
    tx.birthday_discount_applied = True
```

---

### **Issue 4: Session Timeout**

**Problem:**
- Customer session bisa expire saat di tengah checkout

**Solution:**
- Extend session timeout:
```python
SESSION_COOKIE_AGE = 86400 * 7  # 7 hari
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Or implement session renewal:
MIDDLEWARE += ['django.contrib.sessions.middleware.SessionMiddleware']
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only
```

---

### **Issue 5: Notification Delivery**

**Problem:**
- Celery task failure = notifikasi tidak terkirim

**Solution:**
- Implement retry logic:
```python
@shared_task(bind=True, max_retries=3)
def send_notification_task(self, pelanggan_id, ...):
    try:
        # Send logic
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # Retry in 60s
```

---

### **Issue 6: Missing Validation in Views**

**Problem:**
- Views tidak ada `get_notification_count()` helper

**Solution:**
- Implement helper function:
```python
def get_notification_count(pelanggan_id):
    return Notifikasi.objects.filter(
        idPelanggan_id=pelanggan_id,
        is_read=False
    ).count()
```

---

### **Rekomendasi Improvements:**

#### **1. Database Indexing**
```python
class Pelanggan:
    username = CharField(unique=True, db_index=True)
    email = EmailField(unique=True, db_index=True)
    tanggal_lahir = DateField(db_index=True)

class Transaksi:
    status_transaksi = CharField(..., db_index=True)
    tanggal = DateTimeField(..., db_index=True)
    idPelanggan = ForeignKey(..., db_index=True)
```

#### **2. API Endpoints**
```python
# Add REST API untuk mobile app
# /api/v1/products/
# /api/v1/cart/
# /api/v1/orders/
# /api/v1/notifications/
```

#### **3. Caching**
```python
# Cache frequently accessed data
@cache_page(60 * 5)  # 5 minutes
def produk_list(request):
    ...

# Cache diskon calculation
from django.core.cache import cache
diskon_cache = cache.get(f'diskon_{pelanggan_id}')
```

#### **4. Logging**
```python
# Comprehensive logging
logger.info(f"Customer {pelanggan_id} checkout: {total}")
logger.warning(f"Low stock: {produk_id}")
logger.error(f"Payment failed: {transaksi_id}")
```

#### **5. Testing**
```python
# Unit tests untuk critical logic
class DiscountCalculationTest(TestCase):
    def test_p2a_discount(self):
        # Test P2-A logic
        pass
    
    def test_p2b_discount(self):
        # Test P2-B logic
        pass
```

#### **6. Production Deployment**
```
- Use PostgreSQL instead of SQLite
- Implement Redis for caching & Celery
- Use Gunicorn/uWSGI for WSGI server
- Use Nginx for reverse proxy
- SSL/TLS certificates for HTTPS
- Environment variables for secrets
```

---

## 📈 METRICS & KPI

### **Customer Metrics:**
- Total registered customers
- Active customers (last 30 days)
- Average order value
- Customer lifetime value
- Repeat purchase rate

### **Sales Metrics:**
- Total revenue
- Monthly revenue trend
- Top 10 products
- Conversion rate (cart → purchase)
- Abandoned cart rate

### **Operational Metrics:**
- Average order fulfillment time
- On-time delivery rate
- Payment success rate
- Refund rate
- Average feedback rating

---

## 🎯 KESIMPULAN

Proyek **Barokah Jaya Beton** adalah e-commerce system yang well-structured dengan:

✅ **Kekuatan:**
- Clear separation of concerns (Models, Views, Business Logic)
- Multi-tier discount system yang sophisticated
- Real-time notification system
- Session-based authentication untuk scalability
- Atomic transactions untuk data consistency

⚠️ **Areas for Improvement:**
- Add comprehensive error handling
- Implement monitoring & alerting
- Add automated tests
- Optimize database queries
- Implement caching strategy
- Add API endpoints untuk mobile

---

**Laporan dibuat:** 28 November 2025  
**Status:** ✅ Analisis Lengkap Selesai

