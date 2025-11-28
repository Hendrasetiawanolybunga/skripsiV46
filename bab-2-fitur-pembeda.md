# BAB 2: TINJAUAN PUSTAKA DAN FITUR PEMBEDA

## 2.1 Tinjauan Pustaka

Penelitian ini merujuk pada lima artikel yang mengembangkan aplikasi berbasis Web dengan fitur utama seperti pemesanan online, manajemen stok, dan pelaporan penjualan:

1. **Indah Purnama Sari (2022)** - Mengembangkan aplikasi jasa laundry sepatu dengan fokus pada manajemen pesanan dan tracking status pengiriman.

2. **Huzainsyahnoor Aksad & M. Rizwan Ripani (2020)** - Mengembangkan aplikasi penjualan UMKM dengan fitur katalog produk, keranjang belanja, dan manajemen inventaris dasar.

3. **Rerin Wulandari (2021)** - Mengembangkan e-commerce sparepart motor dengan sistem pembayaran manual dan tracking pesanan.

4. **Rachelle Luciana & Dea Andini Andriati (2024)** - Mengembangkan aplikasi penjualan toko tas dengan integrasi e-wallet payment dan sistem review produk berbintang.

5. **Deddy Rudhistiar (2024)** - Mengembangkan aplikasi penjualan paving dan batako dengan fitur manajemen stok dan laporan penjualan sederhana.

Kelima penelitian di atas umumnya menyediakan fitur-fitur dasar seperti:
- Katalog produk dengan kategori
- Sistem keranjang belanja
- Proses checkout dan pembayaran
- Tracking status pesanan
- Manajemen stok produk
- Laporan penjualan agregat

Namun, masing-masing penelitian memiliki fokus yang berbeda sesuai dengan karakteristik bisnis yang mereka targetkan.

---

## 2.2 Fitur Pembeda Penelitian

Penelitian UD. Barokah Jaya Beton ini menawarkan **fitur-fitur pembeda yang komprehensif** yang belum ada atau tidak lengkap dalam kelima artikel tersebut. Berikut adalah penjelasan detail fitur pembeda:

### **2.2.1 Sistem CRM (Customer Relationship Management) Terintegrasi**

**Definisi dan Implementasi:**
CRM adalah sistem yang mengintegrasikan seluruh interaksi dengan pelanggan untuk meningkatkan loyalitas dan kepuasan mereka. Dalam penelitian ini, CRM terintegrasi mencakup:

**a) Pencatatan Data Pelanggan Lengkap:**
- Data demografis: nama, alamat, nomor telepon, email, tanggal lahir
- Tracking data: akun pelanggan dengan session-based authentication
- Implementasi: Model `Pelanggan` dengan 8 field terstruktur

**b) Riwayat Transaksi Terintegrasi:**
- Setiap pelanggan dapat melihat seluruh riwayat transaksi mereka
- Status transaksi real-time: DIPROSES → DIBAYAR → DIKIRIM → SELESAI
- Total spending tracking untuk identifikasi loyal customers
- Implementasi: Model `Transaksi` dan `DetailTransaksi` dengan ForeignKey ke Pelanggan
- View: `daftar_pesanan()` dan `detail_pesanan()` untuk customer tracking

**c) Deteksi Otomatis Loyalitas Pelanggan:**
- Sistem otomatis menghitung total pembelian pelanggan (status DIBAYAR/DIKIRIM/SELESAI)
- Threshold loyalitas: ≥ Rp 5.000.000
- Logika: 
```python
is_loyal = total_spending >= 5000000
```
- Diimplementasikan di views untuk personalisasi pengalaman belanja

**d) Identifikasi Top 3 Produk Favorit:**
- Sistem otomatis mengidentifikasi 3 produk yang paling sering dibeli pelanggan
- Digunakan untuk: personalisasi rekomendasi, perhitungan diskon ulang tahun
- Implementasi method: `Pelanggan.get_top_purchased_products(limit=3)`
- Query kompleks yang menggabungkan Transaksi, DetailTransaksi, dan Produk

**e) Feedback dan Sistem Survei Pelanggan:**
- Pelanggan dapat memberikan feedback untuk setiap pesanan yang selesai
- Feedback dapat disertai dengan foto bukti sebagai dokumentasi
- Implementasi: Fields `feedback` dan `fotofeedback` di Model Transaksi
- Upload path: `/media/feedback_images/`
- View: Integrasi feedback form di halaman `detail_pesanan()`
- Admin dapat review feedback untuk quality assurance

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian terkait tidak mengintegrasikan sistem deteksi loyalitas otomatis
- Tidak ada sistem identifikasi produk favorit per customer
- Tidak ada fitur feedback dengan dokumentasi visual yang terstruktur

---

### **2.2.2 Sistem Diskon Otomatis Berlapis (Multi-Tier Intelligent Discount)**

**Definisi dan Implementasi:**
Sistem diskon berlapis yang mengombinasikan multiple trigger (loyalitas, ulang tahun, nilai keranjang) untuk memberikan penawaran yang personalized dan intelligent.

**a) Diskon Manual oleh Administrator:**
- Admin dapat membuat diskon per produk tertentu atau general untuk semua produk
- Fitur lengkap: set persentase diskon, status aktif/tidak aktif, tanggal expiry
- Scope: SINGLE_PRODUCT atau ALL_PRODUCTS
- Implementasi: Model `DiskonPelanggan` dengan field scope_diskon
- View: Admin dapat manage diskon melalui Django admin interface Jazzmin
- Prioritas: **TERTINGGI** dalam hierarchy diskon

**b) Diskon Loyalitas Otomatis (P1):**
- Trigger: Pelanggan yang total pembeliannya sudah ≥ Rp 5.000.000
- Admin dapat mengatur diskon khusus untuk loyal customers
- Dapat diaplikasikan ke seluruh produk atau produk tertentu
- Prioritas: **MEDIUM** (jika tidak ada diskon manual)

**c) Diskon Ulang Tahun Permanen (P2-A):**
- Trigger: Pelanggan yang ulang tahun HARI INI AND sudah mencapai status loyal
- Diskon otomatis: 10% untuk 3 produk favorit mereka
- Durasi: Selama 24 jam dari ulang tahun
- Logika:
```python
IF is_birthday AND is_loyal:
    Apply 10% discount to top_3_products
```
- Implementasi: Deteksi di views `tambah_ke_keranjang()` dan `proses_pembayaran()`
- Notifikasi otomatis: "Diskon Ulang Tahun Permanen 10% untuk 3 produk terfavorit Anda"
- Scope: `ALL_PRODUCTS` (namun terbatas ke 3 produk favorit)

**d) Diskon Ulang Tahun Instan (P2-B):**
- Trigger: Pelanggan yang ulang tahun HARI INI AND cart total mencapai ≥ Rp 5.000.000
- Berlaku meskipun pelanggan belum pernah mencapai status loyal sebelumnya
- Diskon otomatis: 10% untuk TOTAL BELANJA saat checkout
- Logika:
```python
IF is_birthday AND total_cart_value >= 5000000:
    Apply 10% discount to total_cart
```
- Implementasi: Deteksi di `proses_pembayaran()` sebelum create DetailTransaksi
- Notifikasi otomatis: "Diskon Ulang Tahun Instan 10% untuk SEMUA belanja hari ini"
- Scope: `CART_THRESHOLD` dengan minimum threshold

**e) Sistem Prioritas Diskon:**
Urutan aplikasi diskon (priority hierarchy):
```
Priority 1: Manual Single-Product Discount (tertinggi)
Priority 2: Manual General Discount
Priority 3: ALL_PRODUCTS Discount (P2-A atau manual loyalty)
Priority 4: CART_THRESHOLD Discount (P2-B)
Priority 5: Tidak ada diskon (terendah)
```

**f) Multi-Scope Discount Architecture:**
- `SINGLE_PRODUCT`: Diskon untuk produk spesifik
- `ALL_PRODUCTS`: Diskon untuk semua produk di dalam scope
- `CART_THRESHOLD`: Diskon berdasarkan threshold nilai keranjang

**Implementasi Database:**
```
Model DiskonPelanggan:
- idPelanggan (FK)
- idProduk (FK, NULLABLE) ← NULL = general discount
- persen_diskon (IntegerField)
- status (CharField: 'aktif', 'tidak_aktif')
- scope_diskon (CharField: SINGLE_PRODUCT, ALL_PRODUCTS, CART_THRESHOLD)
- minimum_cart_total (DecimalField, NULLABLE)
- berlaku_sampai (DateTimeField, NULLABLE)
```

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak mengimplementasikan sistem diskon otomatis yang triggered oleh loyalitas dan ulang tahun
- Tidak ada sistem multi-tier/berlapis diskon dengan prioritas hierarchy
- Tidak ada fitur "instant loyalty" yang memungkinkan customer baru mendapat diskon
- Tidak ada scope management untuk flexibility aplikasi diskon

---

### **2.2.3 Sistem Notifikasi Real-Time (WebSocket + Celery)**

**Definisi dan Implementasi:**
Sistem notifikasi terintegrasi yang memberikan informasi real-time kepada pelanggan melalui multiple channels (in-app dan email).

**a) In-App Notification Real-Time:**
- Implementasi: WebSocket menggunakan Django Channels + Daphne ASGI server
- Channel layer: Redis (untuk production) atau in-memory (development)
- Notifikasi ditampilkan langsung di dashboard pelanggan tanpa refresh
- Group-based delivery: `user_{pelanggan_id}` group
- Implementasi Consumer: `consumers.py` dengan WebSocket connect/disconnect/receive
- View: Notifikasi count widget di navbar (helper: `get_notification_count()`)

**b) Background Task Processing:**
- Implementasi: Celery task queue dengan Redis broker
- Task: `send_notification_task(pelanggan_id, tipe_pesan, isi_pesan, url_target)`
- Task ini:
  1. Create record di database (`Notifikasi` model)
  2. Send via WebSocket
  3. Send email notification (jika configured)

**c) Email Notification:**
- Trigger: Event penting (pembayaran dikonfirmasi, pesanan dikirim, promo)
- Template: HTML email dengan CTA (Call-to-Action) link
- Implementasi: `send_notification_email()` function di views
- Email templates: `/templates/emails/`
  - `birthday_discount_email.html`
  - `new_product_email.html`
  - `stock_update_email.html`
- Configuration: Settings.py dengan EMAIL_BACKEND

**d) Notification Events yang Triggered:**

| Event | Trigger | Tipe Notifikasi |
|-------|---------|-----------------|
| Selamat Ulang Tahun | Saat registrasi atau add to cart pada hari ulang tahun | In-app + Email |
| Diskon Ulang Tahun Permanen | Pelanggan loyal pada ulang tahun | In-app + Email |
| Diskon Ulang Tahun Instan | Non-loyal pelanggan mencapai cart ≥ 5jt pada ulang tahun | In-app + Email |
| Pesanan Dibuat | Setelah transaksi sukses di-create | In-app |
| Pembayaran Dikonfirmasi | Admin update status ke DIBAYAR | In-app + Email |
| Pesanan Dikirim | Admin update status ke DIKIRIM | In-app + Email |
| Pesanan Selesai | Karyawan verifikasi pengiriman | In-app + Email |

**e) Notification Storage & Management:**
- Model `Notifikasi` menyimpan semua notifikasi
- Fields: idPelanggan, tipe_pesan, isi_pesan, is_read, created_at, link_cta
- View: `notifikasi()` menampilkan notification center dengan mark as read
- Admin dapat view all notifications untuk audit trail

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak mengimplementasikan WebSocket real-time notification
- Tidak ada integration dengan Celery untuk background task processing
- Tidak ada multi-channel notification (in-app + email)
- Tidak ada CTA (Call-to-Action) link dalam notifikasi
- Tidak ada notification center untuk customer view all notifications

---

### **2.2.4 Sistem Verifikasi Pengiriman dengan Dokumentasi Visual**

**Definisi dan Implementasi:**
Sistem yang memungkinkan karyawan/kurir memverifikasi pengiriman fisik dengan dokumentasi foto untuk meningkatkan transparansi dan kepercayaan pelanggan.

**a) Role Karyawan Terpisah:**
- Model `Karyawan` terpisah dari Django's built-in User
- Fields: id, nama, email, password (hashed), is_active, created_at
- Session-based authentication: `request.session['karyawan_id']`
- Decorator: `@karyawan_required` untuk access control

**b) Karyawan Dashboard:**
- View: `dashboard_karyawan()` 
- Menampilkan list transaksi dengan status DIKIRIM
- Table: Order #, Customer, Total, Shipping Address, Action Button
- Order by: Tanggal transaksi (newest first)

**c) Verifikasi Pengiriman Form:**
- View: `verifikasi_pengiriman(request, pk)`
- Form: `TransaksiVerificationForm`
- Fields:
  1. Upload `foto_pengiriman` (required saat status = SELESAI)
  2. Status transaksi dropdown (DIKIRIM → SELESAI)
- Validation: Foto harus ada jika status = SELESAI
- Upload path: `/media/verifikasi_pengiriman/`

**d) Documentation Trail:**
- Field `foto_pengiriman` di Model Transaksi menyimpan proof of delivery
- Admin dapat review foto untuk quality assurance
- Transparansi: Customer dapat melihat foto pengiriman di detail pesanan

**e) Workflow:**
```
Status DIBAYAR (dari admin approval)
    ↓
[Karyawan mulai pengiriman]
    ↓
Status DIKIRIM (oleh admin sebelum ke karyawan)
    ↓
[Karyawan verifikasi & ambil foto]
    ↓
Form Submit: Upload foto + status SELESAI
    ↓
Status SELESAI (transaksi complete)
    ↓
Notification: Pelanggan dapat submit feedback
```

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak memiliki role karyawan terpisah untuk verifikasi pengiriman
- Tidak ada dokumentasi visual (foto) untuk proof of delivery
- Tidak ada workflow yang terstruktur untuk verifikasi pengiriman
- Tidak ada integration antara karyawan verification dan customer notification

---

### **2.2.5 Stock Management dengan Atomic Transaction**

**Definisi dan Implementasi:**
Sistem manajemen stok yang sophisticated dengan validation di multiple points dan atomic transaction untuk memastikan data consistency.

**a) Validasi Stok Multi-Point:**

| Point | Lokasi | Logic |
|-------|--------|-------|
| Add to Cart | `tambah_ke_keranjang()` | Check jika `current_qty + new_qty <= stok_produk` |
| Cart View | `keranjang()` | Display current stok untuk transparency |
| Checkout | `checkout()` | Final validation sebelum create transaksi |
| Payment | `proses_pembayaran()` | Atomic stock deduction |

**b) Stock Adjustment Logic:**
```python
IF (current_in_cart + requested_qty) > stok_produk:
    available = stok_produk - current_in_cart
    IF available <= 0:
        REJECT: "Stok tidak cukupi"
    ELSE:
        ADJUST: quantity = available
        WARN: "Stok terbatas, dapat menambah {available} unit"
```

**c) Atomic Transaction Implementation:**
```python
WITH transaction.atomic():
    FOR EACH item IN cart:
        produk = Produk.objects.select_for_update().get(pk=id)
        
        IF produk.stok_produk < jumlah:
            RAISE InsufficientStockException
        
        produk.stok_produk -= jumlah
        produk.save()
        
        DetailTransaksi.create(...)
    
    transaksi.total = calculate_total()
    transaksi.save()
    
    IF error:
        ROLLBACK ALL changes
```

**d) Race Condition Prevention:**
- Implementasi `select_for_update()` untuk database lock
- Memastikan concurrent requests tidak cause overselling
- Atomic transaction ensures all-or-nothing behavior

**e) Low Stock Alert:**
- Threshold: Stok < 10 unit
- Display di admin dashboard: `low_stock_products`
- Admin dapat take action sebelum stok habis

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak menerapkan atomic transaction untuk stock deduction
- Tidak ada race condition prevention dengan select_for_update()
- Tidak ada multi-point validation untuk stock consistency
- Tidak ada low stock alert system

---

### **2.2.6 Admin Dashboard Analytics**

**Definisi dan Implementasi:**
Dashboard analytics yang comprehensive untuk mendukung business intelligence dan strategic decision making.

**a) Custom Admin Index:**
- Endpoint: `/admin/` (override default Django admin)
- Framework: Jazzmin untuk enhanced UI/UX
- Replace default Django admin interface dengan custom design

**b) Revenue Analytics:**
- Chart: Bar chart revenue bulanan (6 bulan terakhir)
- Data: Sum(transaksi.total) untuk status DIBAYAR/DIKIRIM/SELESAI
- Filter by date range
- View: `custom_admin_dashboard()`

**c) Transaction Monitoring:**
- Table: 5 transaksi terbaru
- Fields: Order #, Customer, Amount, Status, Date
- Real-time display
- Quick access untuk admin review

**d) Inventory Alerts:**
- Table: Produk dengan stok < 10
- Order by: stok terendah first
- Alert color: Red untuk urgent restocking
- Direct link ke product edit

**e) Best-Selling Products Report:**
- Endpoint: `/laporan/produk-terlaris/`
- Ranking: Top 10 produk by quantity sold
- Data: Product, Qty, Revenue, Percentage
- Filter by period

**f) Detailed Transaction Report:**
- Endpoint: `/laporan/transaksi/`
- Include: Customer, Items, Amount, Status, Date
- Filter: Date range, status, customer
- Exportable (future feature: PDF export)

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak mengimplementasikan custom admin dashboard
- Tidak ada real-time revenue analytics dengan chart visualization
- Tidak ada inventory alert system
- Tidak ada best-selling products ranking
- Tidak ada detailed transaction report dengan filters

---

### **2.2.7 Payment Processing dengan Deadline Management**

**Definisi dan Implementasi:**
Sistem pembayaran yang sophisticated dengan payment deadline dan status tracking.

**a) Payment Form & Upload:**
- Form: `PembayaranForm` dengan bukti_bayar FileField
- Upload path: `/media/bukti_pembayaran/`
- Validation: File type check, file size check
- Implementation: `proses_pembayaran()` view

**b) Payment Deadline (Payment Window):**
- Set otomatis saat transaksi di-create: `waktu_checkout`
- Deadline: `waktu_checkout + 24 hours` = `batas_waktu_bayar`
- Display di payment form untuk transparency
- Fields di Model Transaksi:
  - `waktu_checkout` (DateTimeField)
  - `batas_waktu_bayar` (DateTimeField)

**c) Payment Status Tracking:**
- Status flow:
  1. DIPROSES (default saat transaksi created)
  2. DIBAYAR (admin approve after review bukti_bayar)
  3. DIKIRIM (admin update saat karyawan mulai pengiriman)
  4. SELESAI (karyawan verifikasi pengiriman)
- Admin dapat preview bukti_bayar sebelum approve
- Payment deadline validation untuk auto-cancel (future feature)

**d) Manual Payment Verification:**
- Admin review bukti_bayar di Django admin
- Can see: bank transfer screenshot, amount, date
- Admin update status to DIBAYAR jika verified
- Trigger notification ke customer saat dibayar

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak mengimplementasikan payment deadline tracking
- Tidak ada explicit waktu_checkout dan batas_waktu_bayar fields
- Tidak ada payment window display ke customer
- Tidak ada automated payment deadline enforcement

---

### **2.2.8 Sistem Permintaan Pengiriman Fleksibel**

**Definisi dan Implementasi:**
Opsi pengiriman yang fleksibel sesuai kebutuhan dan preferensi pelanggan.

**a) Opsi Pengiriman:**
1. **Pengiriman oleh UD. Barokah Jaya Beton:**
   - Dikelola oleh karyawan terstruktur
   - Verifikasi dengan dokumentasi visual (foto)
   - Tracking real-time melalui status transaksi
   
2. **Pengambilan Langsung oleh Pelanggan:**
   - Pelanggan ambil ke lokasi UD.
   - Tidak memerlukan pengiriman
   - Dapat di-set di form checkout

**b) Shipping Address Management:**
- Form: Alamat pengiriman custom per transaksi
- Default: Auto-fill dari profile customer address
- Validation: Address tidak boleh kosong
- Field di Model Transaksi: `alamat_pengiriman`

**c) Shipping Cost:**
- Field: `ongkir` (DecimalField) di Model Transaksi
- Default: 0 (untuk pickup atau local delivery)
- Admin dapat set per transaksi jika ada biaya khusus

**d) Workflow:**
```
Customer checkout
    ↓
Select delivery option:
    - Delivery by UD (with address input)
    - Pickup by customer
    ↓
Input/confirm shipping address
    ↓
Set shipping cost (if any)
    ↓
Proceed to payment
```

**Keunggulan dibanding penelitian sebelumnya:**
- Kelima penelitian tidak mengimplementasikan flexible shipping options
- Tidak ada opsi pickup oleh customer
- Tidak ada manajemen karyawan untuk delivery verification
- Tidak ada structured delivery workflow

---

## 2.3 Ringkasan Perbandingan Fitur

| Fitur | Penelitian Sebelumnya | Penelitian Ini |
|-------|----------------------|----------------|
| Katalog Produk | ✅ Ada | ✅ Ada + Kategori |
| Keranjang Belanja | ✅ Ada | ✅ Ada + Validasi Stok |
| Pemesanan | ✅ Ada | ✅ Ada + Deadline |
| Pembayaran Manual | ✅ Ada | ✅ Ada + Deadline Tracking |
| Tracking Pesanan | ✅ Ada (basic) | ✅ Ada + Real-time Status |
| **CRM Terintegrasi** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Loyalitas Otomatis** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Diskon Berlapis** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Ulang Tahun Detection** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **WebSocket Notification** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Email Notification** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Karyawan Verification** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| **Foto Delivery Proof** | ❌ Tidak | ✅ **YA (UNIQUE)** |
| Manajemen Stok | ✅ Ada (basic) | ✅ Ada + Atomic Transaction |
| Laporan Penjualan | ✅ Ada (basic) | ✅ Ada + Analytics Dashboard |
| Feedback Pelanggan | ❌ Tidak | ✅ **YA (UNIQUE)** |
| Admin Dashboard | ✅ Ada (default) | ✅ Ada + Custom Jazzmin |

---

## 2.4 Kesimpulan Fitur Pembeda

Penelitian UD. Barokah Jaya Beton **menawarkan 8 fitur pembeda utama** yang tidak ada atau tidak lengkap dalam kelima penelitian sebelumnya:

1. **✅ CRM Terintegrasi** dengan loyalty detection otomatis
2. **✅ Diskon Berlapis Intelligent** (P2-A, P2-B) dengan priority hierarchy
3. **✅ WebSocket Real-time Notification** untuk in-app updates
4. **✅ Email Notification** terintegrasi dengan Celery
5. **✅ Karyawan Verification System** dengan role terpisah
6. **✅ Dokumentasi Visual Pengiriman** (foto proof of delivery)
7. **✅ Atomic Transaction Stock Management** untuk data consistency
8. **✅ Analytics Dashboard** dengan real-time insights

Kombinasi dari fitur-fitur ini menciptakan **complete ecosystem** yang tidak hanya fokus pada e-commerce transactions, tetapi juga pada **customer relationship management, business intelligence, dan operational transparency**. Hal ini membuat penelitian ini memberikan kontribusi signifikan dalam pengembangan sistem e-commerce untuk UMKM yang lebih sophisticated dan customer-centric.

