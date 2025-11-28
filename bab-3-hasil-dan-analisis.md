# BAB 3: HASIL YANG DIHARAPKAN DAN ANALISIS KEBUTUHAN SISTEM

## 3.1 Hasil yang Diharapkan

Hasil yang diharapkan dari penelitian ini adalah sebuah aplikasi pemesanan dan penjualan berbasis Web yang dapat digunakan oleh UD. Barokah Jaya Beton untuk meningkatkan efisiensi operasional dan kepuasan pelanggan. Adapun rincian hasil yang ingin dicapai antara lain:

### **3.1.1 Aplikasi Web untuk Pemesanan Produk Online**

Aplikasi ini memfasilitasi proses pemesanan produk beton secara online dengan fitur-fitur berikut:

a. **Katalog Produk Lengkap:**
   - Display semua produk dengan foto, deskripsi, harga, dan ketersediaan stok
   - Filter berdasarkan kategori produk
   - Detail produk dengan informasi lengkap
   - Implementasi: Templates `product_list.html`, `product_detail.html`, `beranda_umum.html`

b. **Sistem Keranjang Belanja:**
   - Pelanggan dapat menambah/mengurangi/menghapus produk dari keranjang
   - Validasi stok otomatis mencegah overselling
   - Session-based cart management
   - Real-time calculation harga dan diskon
   - Implementasi: View `tambah_ke_keranjang()`, `keranjang()`, `update_keranjang()`

c. **Proses Checkout Terstruktur:**
   - Form pemesanan dengan alamat pengiriman
   - Upload bukti pembayaran
   - Opsi metode pengiriman (delivery oleh UD atau pickup)
   - Automatic payment deadline 24 jam
   - Atomic transaction untuk data consistency
   - Implementasi: View `checkout()`, `proses_pembayaran()`

d. **Akses 24/7:**
   - Pelanggan dapat melakukan pemesanan kapan saja dan di mana saja
   - Responsive design untuk desktop dan mobile
   - Tidak memerlukan datang langsung ke lokasi usaha
   - Implementasi: Django development server dengan Daphne ASGI

e. **Notifikasi Pemesanan:**
   - Pelanggan menerima notifikasi saat pesanan dibuat, dibayar, dikirim, dan selesai
   - In-app notification real-time
   - Email notification untuk event penting
   - Implementasi: Celery tasks + WebSocket (Channels/Daphne)

---

### **3.1.2 Sistem Manajemen Stok Otomatis Real-Time**

Sistem ini mencatat keluar-masuknya produk secara otomatis dan mengurangi kesalahan pencatatan manual:

a. **Tracking Stok Real-Time:**
   - Setiap penambahan ke keranjang tercatat di session
   - Setiap checkout mengurangi stok produk secara atomic
   - Admin dapat melihat stok current di dashboard
   - Implementasi: Field `stok_produk` di Model Produk

b. **Multi-Point Validation:**
   - Validasi saat add to cart: `tambah_ke_keranjang()` cek stok tersedia
   - Validasi saat checkout: `checkout()` final validation
   - Validasi saat payment: `proses_pembayaran()` atomic deduction
   - Mencegah overselling dengan `select_for_update()` database lock

c. **Low Stock Alert:**
   - Automatic alert untuk produk dengan stok < 10 unit
   - Display di admin dashboard: `low_stock_products` table
   - Threshold configurable di STOK_KRITIS_THRESHOLD constant
   - Implementasi: View `custom_admin_dashboard()`

d. **Stock Deduction History:**
   - Setiap transaksi mencatat detil produk dan quantity di DetailTransaksi
   - Admin dapat track stock movement per transaksi
   - Tidak ada duplikasi atau hilang data
   - Implementasi: Model DetailTransaksi dengan ForeignKey ke Transaksi & Produk

e. **Eliminasi Kesalahan Manual:**
   - Tidak ada pencatatan manual di buku
   - Data otomatis tersimpan di database
   - Reducing human error dan data loss risk
   - Implementasi: Atomic transaction dengan rollback capability

---

### **3.1.3 Fitur CRM (Customer Relationship Management) Terintegrasi**

Fitur CRM mencatat data pelanggan, riwayat transaksi, dan memfasilitasi komunikasi:

a. **Pencatatan Data Pelanggan Lengkap:**
   - Nama, alamat, nomor telepon, email, tanggal lahir
   - Data tersimpan terstruktur di database
   - Implementasi: Model Pelanggan dengan 8 field terstruktur

b. **Riwayat Transaksi Lengkap:**
   - Pelanggan dapat melihat semua transaksi mereka di halaman Pesanan
   - Detail pesanan: produk, harga, diskon, total, status, tanggal
   - Status tracking real-time: DIPROSES → DIBAYAR → DIKIRIM → SELESAI
   - Implementasi: View `daftar_pesanan()`, `detail_pesanan()`

c. **Deteksi Loyalitas Otomatis:**
   - Sistem menghitung total spending pelanggan
   - Threshold: ≥ Rp 5.000.000 = loyal customer
   - Digunakan untuk personalisasi diskon dan rekomendasi
   - Implementasi: Query `Transaksi.objects.filter(status_transaksi__in=['DIBAYAR', 'DIKIRIM', 'SELESAI']).aggregate(Sum('total'))`

d. **Identifikasi Produk Favorit:**
   - Sistem otomatis mengidentifikasi 3 produk yang paling sering dibeli
   - Digunakan untuk rekomendasi dan diskon ulang tahun P2-A
   - Implementasi: Method `Pelanggan.get_top_purchased_products(limit=3)`

e. **Feedback dan Sistem Survei:**
   - Pelanggan dapat memberikan feedback untuk setiap pesanan yang selesai
   - Feedback dapat disertai dengan foto bukti
   - Admin dapat review feedback untuk quality assurance
   - Implementasi: Fields `feedback` dan `fotofeedback` di Model Transaksi, Form di `detail_pesanan()`

f. **Komunikasi Terintegrasi:**
   - Notifikasi otomatis saat ada update pesanan
   - In-app notification center untuk melihat semua notifikasi
   - Email notification untuk event penting
   - Implementasi: Model Notifikasi, View `notifikasi()`

g. **Deteksi Ulang Tahun Otomatis:**
   - Sistem mendeteksi pelanggan yang ulang tahun hari ini
   - Mengirimkan notifikasi ucapan dan info diskon
   - Trigger diskon otomatis P2-A atau P2-B
   - Implementasi: Field `tanggal_lahir`, logic di `tambah_ke_keranjang()` dan `proses_pembayaran()`

---

### **3.1.4 Fitur Pelaporan Penjualan dan Analisis Data**

Fitur ini membantu pemilik usaha membuat keputusan strategis berbasis data:

a. **Dashboard Analytics:**
   - Custom admin dashboard override default Django admin
   - Menampilkan key metrics real-time
   - Framework: Jazzmin untuk enhanced UI
   - Implementasi: View `custom_admin_dashboard()`

b. **Revenue Analytics:**
   - Chart revenue bulanan (6 bulan terakhir)
   - Data: Sum(transaksi.total) untuk status DIBAYAR/DIKIRIM/SELESAI
   - Visualization: Bar chart menggunakan Chart.js
   - Trend analysis untuk business forecasting
   - Implementasi: Query dengan TruncMonth, Chart.js di template

c. **Transaction Monitoring:**
   - Table 5 transaksi terbaru di dashboard
   - Fields: Order #, Customer, Amount, Status, Date
   - Real-time display untuk quick overview
   - Direct access untuk admin review
   - Implementasi: View `custom_admin_dashboard()`, Query dengan `select_related()`

d. **Inventory Intelligence:**
   - Low stock alert table untuk produk < 10 unit
   - Display order by stok terendah
   - Quick access untuk restocking decision
   - Implementasi: Query `Produk.objects.filter(stok_produk__lt=STOK_KRITIS_THRESHOLD)`

e. **Best-Selling Products Report:**
   - Endpoint: `/laporan/produk-terlaris/`
   - Ranking: Top 10 produk by quantity sold
   - Data: Product name, Qty, Revenue, Percentage of total
   - Filter by date range
   - Implementasi: View `laporan_produk_terlaris()`, Aggregation query dengan Sum()

f. **Detailed Transaction Report:**
   - Endpoint: `/laporan/transaksi/`
   - Include: Customer, Items, Amount, Discount, Status, Date
   - Filter: Date range, status, customer
   - Export capability (future: PDF export dengan reportlab)
   - Implementasi: View `laporan_transaksi()`, Template dengan filters

g. **Data-Driven Decision Making:**
   - Insights untuk product mix optimization
   - Customer segment analysis
   - Seasonal trend detection
   - Pricing strategy support

---

### **3.1.5 Integrasi Sistem Pengiriman Barang Fleksibel**

Sistem ini memungkinkan pelanggan memilih metode pengiriman sesuai preferensi:

a. **Opsi Pengiriman Fleksibel:**
   - **Delivery oleh UD. Barokah Jaya Beton:** Karyawan mengantar ke alamat pelanggan
   - **Pickup oleh Pelanggan:** Pelanggan mengambil langsung ke lokasi UD
   - Kedua opsi tersedia saat checkout
   - Implementasi: Form field di halaman checkout

b. **Manajemen Karyawan Terstruktur:**
   - Model Karyawan terpisah dengan role khusus
   - Session-based authentication untuk karyawan
   - Dashboard karyawan untuk list pengiriman
   - Implementasi: Model Karyawan, View `login_karyawan()`, `dashboard_karyawan()`

c. **Verifikasi Pengiriman dengan Dokumentasi:**
   - Karyawan upload foto pengiriman sebagai proof of delivery
   - Transparent delivery tracking untuk customer
   - Quality assurance trail untuk admin
   - Implementasi: Form `TransaksiVerificationForm`, Field `foto_pengiriman`, View `verifikasi_pengiriman()`

d. **Shipping Address Management:**
   - Pelanggan input alamat pengiriman custom per transaksi
   - Default: Auto-fill dari profile address
   - Validation: Address tidak boleh kosong
   - Implementasi: Form field `alamat_pengiriman` di payment form

e. **Shipping Cost Configuration:**
   - Field `ongkir` di Model Transaksi untuk biaya pengiriman
   - Default: 0 untuk pickup atau local delivery
   - Admin dapat set per transaksi jika ada biaya khusus
   - Implementasi: Field DecimalField di Model Transaksi

f. **Delivery Workflow Terstruktur:**
   - Status flow: DIPROSES → DIBAYAR → DIKIRIM → SELESAI
   - Each status tracked dengan timestamp
   - Notification sent ke customer pada setiap status change
   - Implementasi: Status choices di Model Transaksi, Signal handlers untuk notification

g. **Kenyamanan dan Fleksibilitas:**
   - Customer dapat pilih metode sesuai preferensi
   - Karyawan dapat manage delivery dengan terstruktur
   - Admin dapat monitor pengiriman real-time
   - Implementasi: Centralized system untuk coordinate delivery

---

### **3.1.6 User Interface Responsif dan User-Friendly**

Antarmuka dirancang untuk kemudahan akses oleh pelanggan dan admin:

a. **Responsive Design:**
   - Desain menggunakan Bootstrap 5
   - Layout responsive di desktop (1920px+), tablet (768px), mobile (320px+)
   - Navigation adapts ke ukuran screen
   - Implementasi: HTML template dengan Bootstrap grid system

b. **Intuitive Navigation:**
   - Top navbar dengan logo, menu kategori, cart icon, user menu
   - Breadcrumb navigation untuk orientasi user
   - Clear CTA (Call-to-Action) buttons
   - Implementasi: Template `base.html`, `navbar_public.html`

c. **User-Friendly Forms:**
   - Form validation dengan error messages jelas
   - Auto-fill fields untuk registered users
   - Progress indicator untuk multi-step forms (checkout)
   - Implementasi: Django forms dengan Bootstrap styling

d. **Dashboard Clarity:**
   - Admin dashboard menampilkan key metrics dalam cards
   - Charts dengan clear labeling
   - Tables dengan sorting dan filtering
   - Implementasi: Template `admin_index_override.html`, Jazzmin UI

e. **Mobile Optimization:**
   - Touch-friendly buttons (min 48x48 px)
   - Optimized images untuk fast loading
   - Mobile-first navigation
   - Implementasi: CSS media queries, responsive images

f. **Accessibility:**
   - Color contrast sesuai WCAG standards
   - Alt text untuk images
   - Semantic HTML untuk screen readers
   - Implementasi: Best practices di HTML templates

g. **Performance Optimization:**
   - Static files caching (CSS, JS)
   - Database query optimization dengan select_related() dan prefetch_related()
   - Session-based data handling untuk fast loading
   - Implementasi: Django optimization techniques

---

## 3.2 Analisis Kebutuhan Sistem

Analisis kebutuhan sistem bertujuan untuk mengidentifikasi komponen-komponen yang diperlukan dalam perancangan dan pengembangan aplikasi. Analisis ini menjadi dasar untuk memastikan sistem dapat berfungsi sesuai dengan kebutuhan bisnis dan teknis.

---

## 3.3 Analisis Kebutuhan Berdasarkan Tiga Dimensi

### **3.3.1 Analisis Peran Pengguna (User Roles Analysis)**

Peran pengguna menggambarkan jenis-jenis pengguna yang akan berinteraksi dengan sistem, beserta hak akses dan aktivitas yang dapat dilakukan. Dalam aplikasi ini, terdapat **tiga peran pengguna utama**:

#### **A. Admin (Pemilik Usaha)**

Admin memiliki akses penuh terhadap seluruh sistem dan bertanggung jawab dalam operasional dan pengelolaan data:

| Aktivitas | Deskripsi | Implementasi |
|-----------|-----------|--------------|
| **1. Mengelola Data Produk** | Tambah, ubah, hapus produk | Django admin dengan Jazzmin UI |
| a. Tambah produk | Input nama, deskripsi, harga, kategori, foto | Model Produk, Form di admin |
| b. Ubah produk | Edit informasi produk | Admin change_view |
| c. Hapus produk | Hapus produk dari sistem | Admin delete_view |
| d. Set kategori | Assign produk ke kategori | ForeignKey ke Kategori |
| **2. Mengelola Data Pesanan** | View, filter, update status pesanan | Django admin Transaksi list |
| a. View pesanan | Lihat semua pesanan dengan filter | List view dengan filters |
| b. Verify pembayaran | Review bukti_bayar dan approve | Change status ke DIBAYAR |
| c. Update status | Update status pesanan ke DIKIRIM | Change status transaksi |
| d. View detail | Lihat detail pesanan lengkap | Detail view with inline details |
| **3. Akses Laporan & Analytics** | View dashboard, laporan penjualan | Custom admin dashboard |
| a. Revenue dashboard | Lihat chart revenue bulanan | View `custom_admin_dashboard()` |
| b. Transaction report | Lihat detail transaksi | View `laporan_transaksi()` |
| c. Best sellers report | Lihat produk terlaris | View `laporan_produk_terlaris()` |
| d. Export reports | Download report data | Future: PDF export |
| **4. Mengelola Stok Barang** | View stok, low stock alert | Admin Produk list view |
| a. View stok current | Lihat stok real-time | Field di list display |
| b. Low stock alert | Alert produk dengan stok < 10 | Table di dashboard |
| c. Restock decision | Buat keputusan restock | Based on sales trend |
| **5. Mengelola Data Pelanggan** | View data, loyalty status, feedback | Admin Pelanggan list view |
| a. View pelanggan | Lihat semua data pelanggan | List view dengan 6 fields display |
| b. View transaksi | Lihat riwayat transaksi pelanggan | List filter by customer |
| c. View loyalitas | Lihat status loyal pelanggan | Admin method `is_ultah()`, `total_belanja_admin()` |
| d. Review feedback | Lihat feedback dari customer | Transaksi feedback field |
| e. Set diskon | Membuat diskon khusus per customer | Create DiskonPelanggan |
| **6. Manajemen Diskon** | Create, edit, delete diskon | Admin DiskonPelanggan |
| a. Create diskon | Buat diskon manual | Model form di admin |
| b. Set scope | Pilih scope diskon (SINGLE/ALL/THRESHOLD) | CharField choices |
| c. Set expiry | Tentukan berlaku sampai date | DateTimeField |
| d. Action: Birthday diskon | Trigger diskon untuk ulang tahun | Bulk action di admin |

**Akses Control:** Admin login via Django admin dengan is_staff=True

---

#### **B. Pelanggan (Customer)**

Pelanggan berperan sebagai pengguna akhir yang menggunakan sistem untuk melakukan transaksi:

| Aktivitas | Deskripsi | Implementasi |
|-----------|-----------|--------------|
| **1. Manajemen Akun** | Register, login, edit profile | Session-based auth |
| a. Register | Membuat akun baru | View `register_pelanggan()`, Form `PelangganRegistrationForm` |
| b. Login | Login dengan username & password | View `login_pelanggan()`, Form `PelangganLoginForm` |
| c. Logout | Keluar dari akun | View `logout_pelanggan()` |
| d. Edit profil | Update data personal | View `akun()`, Form `PelangganEditForm` |
| **2. Browse Produk** | Lihat katalog, filter kategori | Views publik |
| a. Home | Lihat landing page dengan featured products | View `beranda_umum()` |
| b. Product list | Lihat semua produk | View `produk_list()` |
| c. Filter kategori | Filter produk by kategori | GET param `kategori_id` |
| d. View detail | Lihat detail produk lengkap | View `produk_detail()` |
| e. View diskon | Lihat diskon yang berlaku | Display di product card |
| **3. Pemesanan Produk** | Add to cart, checkout, pay | E-commerce workflow |
| a. Add to cart | Tambah produk ke keranjang | View `tambah_ke_keranjang()` |
| b. View cart | Lihat isi keranjang & total | View `keranjang()` |
| c. Update qty | Ubah jumlah produk | View `update_keranjang()` |
| d. Remove item | Hapus produk dari cart | View `hapus_dari_keranjang()` |
| e. Checkout | Proses checkout | View `checkout()` |
| f. Payment | Upload bukti bayar | View `proses_pembayaran()`, Form `PembayaranForm` |
| g. Select pengiriman | Pilih metode pengiriman | Form field di checkout |
| **4. Tracking Pesanan** | Lihat riwayat, detail, status | Customer orders area |
| a. Order list | Lihat semua pesanan | View `daftar_pesanan()` |
| b. Order detail | Lihat detail pesanan | View `detail_pesanan()` |
| c. Status tracking | Lihat status real-time | Status display di template |
| d. Payment deadline | Lihat batas waktu bayar | Display di payment form |
| **5. Feedback & Komunikasi** | Submit feedback, view notifikasi | Engagement features |
| a. Submit feedback | Berikan feedback untuk pesanan | Form di `detail_pesanan()` |
| b. Add photo | Attach foto dengan feedback | File upload field |
| c. View notifikasi | Lihat semua notifikasi | View `notifikasi()` |
| d. Mark as read | Tandai notifikasi sebagai dibaca | Bulk action di template |
| **6. Dapatkan Diskon** | Birthday diskon, loyalty diskon | Automatic application |
| a. Birthday diskon | Otomatis diskon saat ulang tahun | Trigger di checkout |
| b. Loyalty rewards | Diskon untuk loyal customers | Automatic calculation |
| c. View eligible diskon | Lihat diskon yang tersedia | Display di product & cart |

**Akses Control:** Pelanggan login via session dengan decorator `@login_required_pelanggan`

---

#### **C. Karyawan (Employee - Delivery Staff)**

Karyawan memiliki akses khusus untuk verifikasi pengiriman:

| Aktivitas | Deskripsi | Implementasi |
|-----------|-----------|--------------|
| **1. Manajemen Akun Karyawan** | Login karyawan | Session-based auth terpisah |
| a. Login | Login dengan email & password | View `login_karyawan()`, Form `KaryawanLoginForm` |
| b. Logout | Keluar dari akun | View `logout_karyawan()` |
| **2. Dashboard Pengiriman** | Lihat list pesanan untuk dikirim | Karyawan-specific interface |
| a. View daftar pesanan | Lihat pesanan status DIKIRIM | View `dashboard_karyawan()` |
| b. Pesanan details | Lihat detail pesanan (customer, address, items) | Table dengan quick view |
| **3. Verifikasi Pengiriman** | Upload foto & update status | Delivery verification workflow |
| a. Open verifikasi form | Buka form untuk pesanan tertentu | View `verifikasi_pengiriman()` |
| b. Upload foto | Ambil foto bukti pengiriman | File upload field |
| c. Update status | Ubah status ke SELESAI | Status dropdown |
| d. Submit | Submit verifikasi | Form save ke database |
| **4. Notifikasi** | Terima notification saat ada order baru | System notifications |

**Akses Control:** Karyawan login via session dengan decorator `@karyawan_required`, Model Karyawan terpisah

---

### **3.3.2 Analisis Peran Sistem (System Functional Requirements)**

Peran sistem menjelaskan fungsi-fungsi utama yang dijalankan oleh sistem untuk memenuhi kebutuhan pengguna dan bisnis. Adapun fungsi-fungsi tersebut adalah sebagai berikut:

| # | Fungsi Sistem | Deskripsi | Implementasi |
|---|---------------|-----------|--------------|
| **1** | **Product Catalog Management** | Menyediakan katalog produk online | |
| 1.1 | Display produk | Tampilkan semua produk dengan foto, harga, stok | Template `product_list.html`, View `produk_list()` |
| 1.2 | Filter kategori | Filter produk berdasarkan kategori | GET param `kategori`, Query filter |
| 1.3 | Detail produk | Tampilkan detail lengkap per produk | View `produk_detail()`, Template `product_detail.html` |
| 1.4 | Search kategori | Cari produk by kategori | Query `Produk.objects.filter(kategori__id=kategori_id)` |
| **2** | **Shopping Cart Management** | Mengelola keranjang belanja pelanggan | |
| 2.1 | Add to cart | Tambah produk ke keranjang | View `tambah_ke_keranjang()`, Session-based storage |
| 2.2 | Update qty | Update jumlah produk | View `update_keranjang()`, POST action |
| 2.3 | Remove item | Hapus produk dari keranjang | View `hapus_dari_keranjang()` |
| 2.4 | View cart | Tampilkan isi dan total | View `keranjang()`, Calculate subtotal & discount |
| 2.5 | Stock validation | Validasi stok saat add/checkout | Check `stok_produk >= jumlah` |
| **3** | **Order Processing** | Memproses pesanan dari awal hingga selesai | |
| 3.1 | Create order | Buat transaksi baru | View `proses_pembayaran()`, Create Transaksi record |
| 3.2 | Set payment deadline | Set 24-hour payment window | `batas_waktu_bayar = waktu_checkout + 24h` |
| 3.3 | Update stok | Kurangi stok saat order confirmed | Atomic transaction, `produk.stok_produk -= jumlah` |
| 3.4 | Calculate total | Hitung total dengan diskon & ongkir | Sum all DetailTransaksi + ongkir |
| 3.5 | Payment processing | Process pembayaran transfer bank | Accept bukti_bayar file upload |
| **4** | **Stock Management** | Mengelola stok produk real-time | |
| 4.1 | Track stok | Catat stok real-time | Query `stok_produk` di database |
| 4.2 | Low stock alert | Alert stok rendah | Filter `stok_produk < 10`, Display di dashboard |
| 4.3 | Stock history | Lihat perubahan stok per transaksi | DetailTransaksi mencatat setiap perubahan |
| 4.4 | Prevent overselling | Cegah penjualan melebihi stok | `select_for_update()` database lock |
| **5** | **CRM Features** | Customer Relationship Management | |
| 5.1 | Customer data | Catat data pelanggan lengkap | Model Pelanggan dengan 8 fields |
| 5.2 | Transaction history | Catat riwayat transaksi | Model Transaksi & DetailTransaksi |
| 5.3 | Loyalty detection | Deteksi pelanggan loyal otomatis | Calculate `total_spending >= 5000000` |
| 5.4 | Top products | Identifikasi 3 produk favorit | Method `get_top_purchased_products()` |
| 5.5 | Feedback system | Terima feedback dari customer | Fields `feedback`, `fotofeedback` di Transaksi |
| 5.6 | Birthday detection | Deteksi ulang tahun pelanggan | Compare `tanggal_lahir` dengan hari ini |
| **6** | **Discount Management** | Sistem diskon berlapis otomatis | |
| 6.1 | Manual discount | Admin buat diskon manual | Model DiskonPelanggan, Admin form |
| 6.2 | Loyalty discount | Diskon otomatis untuk loyal | P1: `is_loyal → apply_discount` |
| 6.3 | Birthday discount P2-A | Diskon ulang tahun loyal | P2-A: `is_birthday AND is_loyal → 10% top3` |
| 6.4 | Birthday discount P2-B | Diskon ulang tahun instant | P2-B: `is_birthday AND cart>=5jt → 10% total` |
| 6.5 | Discount priority | Apply diskon sesuai prioritas | Hierarchy: Manual > Loyalty > Birthday > None |
| 6.6 | Discount scope | Manage scope diskon | SINGLE_PRODUCT, ALL_PRODUCTS, CART_THRESHOLD |
| **7** | **Notification System** | Sistem notifikasi real-time & email | |
| 7.1 | In-app notification | Notifikasi langsung di app | WebSocket (Channels/Daphne) |
| 7.2 | Email notification | Kirim email penting | Celery task + Django email backend |
| 7.3 | Event triggers | Trigger notifikasi per event | Payment approved, shipped, birthday |
| 7.4 | Notification center | Tampilkan semua notifikasi | View `notifikasi()`, Model Notifikasi |
| 7.5 | Background tasks | Process notifikasi di background | Celery `send_notification_task()` |
| **8** | **Delivery Management** | Mengelola pengiriman | |
| 8.1 | Delivery options | Pilih metode pengiriman | Delivery by UD or Pickup by customer |
| 8.2 | Shipping address | Input alamat pengiriman | Form field `alamat_pengiriman` |
| 8.3 | Verification form | Form verifikasi pengiriman | View `verifikasi_pengiriman()` |
| 8.4 | Proof of delivery | Upload foto pengiriman | Field `foto_pengiriman`, File upload |
| 8.5 | Delivery tracking | Track status pengiriman | Status: DIKIRIM → SELESAI |
| **9** | **Reporting & Analytics** | Laporan penjualan dan analisis data | |
| 9.1 | Revenue chart | Chart revenue bulanan | Chart.js visualization, 6 months |
| 9.2 | Sales report | Laporan penjualan detail | View `laporan_transaksi()` |
| 9.3 | Best sellers | Produk terlaris ranking | View `laporan_produk_terlaris()` |
| 9.4 | Admin dashboard | Custom admin dashboard | View `custom_admin_dashboard()` |
| 9.5 | Export reports | Export laporan | Future: PDF export capability |
| **10** | **User Authentication** | Sistem login untuk semua role | |
| 10.1 | Customer registration | Register pelanggan baru | View `register_pelanggan()`, Form validation |
| 10.2 | Customer login | Login pelanggan | View `login_pelanggan()`, Session storage |
| 10.3 | Employee login | Login karyawan | View `login_karyawan()`, Model Karyawan |
| 10.4 | Admin login | Login admin | Django default auth + is_staff check |
| 10.5 | Logout | Logout semua role | Clear session, Redirect to home |

---

### **3.3.3 Analisis Kebutuhan Perangkat Lunak (Software Requirements)**

Analisis perangkat lunak menjelaskan tools dan aplikasi yang digunakan dalam proses pengembangan serta pelaksanaan sistem. Berikut adalah perangkat lunak yang digunakan:

| Kategori | Tool/Aplikasi | Versi | Fungsi |
|----------|---------------|-------|--------|
| **Operating System** | Windows 10 | 10.0 | Development & testing environment |
| **Programming Language** | Python | 3.8+ | Backend development |
| **Web Framework** | Django | 4.2.x | Web application framework |
| **Database** | SQLite3 | 3.x | Development database |
| | MySQL | 5.7+ | Production database (recommended) |
| **Real-time Communication** | Channels | 3.0+ | WebSocket support untuk Django |
| | Daphne | 3.0+ | ASGI server untuk Channels |
| **Background Tasks** | Celery | 5.0+ | Background task queue |
| | Redis | 5.0+ | Message broker untuk Celery |
| **Admin UI Framework** | Jazzmin | 2.6+ | Enhanced Django admin interface |
| **Frontend Framework** | Bootstrap | 5.x | Responsive CSS framework |
| **Chart Visualization** | Chart.js | 3.x | Charting library untuk dashboard |
| **ORM** | Django ORM | Built-in | Database abstraction layer |
| **Authentication** | Django Auth | Built-in | User authentication & permissions |
| **Email Backend** | Django Mail | Built-in | Email sending capability |
| **Form Validation** | Django Forms | Built-in | Server-side form validation |
| **Session Management** | Django Sessions | Built-in | Session storage & management |
| **Web Server (Development)** | Django Dev Server | Built-in | Testing & development |
| **Web Server (Production)** | Gunicorn | 19.0+ | Python WSGI HTTP server |
| | Nginx | 1.18+ | Reverse proxy & static file server |
| **Browser** | Google Chrome | Latest | Testing & development browser |
| | Firefox | Latest | Browser compatibility testing |
| | Safari | Latest | Browser compatibility testing |
| **Code Editor** | Visual Studio Code | Latest | Code development IDE |
| **Version Control** | Git | 2.x | Source code management |
| **Package Manager** | Pip | 20.0+ | Python package management |
| **Virtual Environment** | Venv | Built-in | Python environment isolation |
| **File Storage** | Local Filesystem | - | Development file storage |
| | AWS S3 / MinIO | - | Production file storage (optional) |

**Development Stack Summary:**
- **Backend:** Django 4.2 + Python 3.8+
- **Real-time:** Channels + Daphne + Redis
- **Task Queue:** Celery + Redis
- **Database:** SQLite3 (dev) / MySQL (production)
- **Frontend:** Bootstrap 5 + Chart.js
- **Admin UI:** Jazzmin
- **Server:** Gunicorn + Nginx (production)

---

### **3.3.4 Analisis Kebutuhan Perangkat Keras (Hardware Requirements)**

Analisis kebutuhan perangkat keras ini ditujukan untuk pengguna (admin dan pelanggan) yang akan mengakses aplikasi penjualan dan pemesanan berbasis Web. Karena aplikasi berbasis Web dapat dijalankan melalui browser, maka perangkat keras yang dibutuhkan tergolong ringan dan umum dimiliki oleh pengguna.

#### **A. Spesifikasi Minimum untuk Client (User Device)**

Berikut spesifikasi minimum perangkat keras yang direkomendasikan untuk mengakses aplikasi:

| Hardware | Minimum | Recommended |
|----------|---------|-------------|
| **Processor** | Dual-Core (Intel Pentium, Core i3) | Quad-Core atau lebih (Core i5+) |
| **RAM** | 4 GB | 8 GB atau lebih |
| **Storage** | 512 MB free space (cache) | 2 GB free space |
| **Internet Connection** | 2 Mbps | 5 Mbps atau lebih |
| **Screen Size** | 5 inci (mobile) | 13 inci atau lebih (laptop) |
| **Browser** | Chrome/Firefox/Safari (latest 2 versions) | Latest stable version |

**Supported Devices:**
- Desktop (1920x1080 dan lebih)
- Laptop (1366x768, 1920x1080)
- Tablet (768x1024)
- Smartphone (320x568 dan lebih)

#### **B. Spesifikasi Server (Development)**

Untuk menjalankan aplikasi di environment development:

| Hardware | Spesifikasi |
|----------|------------|
| **Processor** | Intel Core i5 / Ryzen 5 (2.4 GHz+) |
| **RAM** | 8 GB minimum, 16 GB recommended |
| **Storage** | 50 GB SSD untuk project + database |
| **Internet** | Broadband connection (10 Mbps+) |
| **OS** | Windows 10/11, macOS, atau Linux |

#### **C. Spesifikasi Server (Production)**

Untuk menjalankan aplikasi di environment production (recommended):

| Hardware | Spesifikasi |
|----------|------------|
| **Processor** | Intel Xeon E5 / AMD EPYC (2.5 GHz+, 4 cores) |
| **RAM** | 16 GB minimum, 32 GB recommended |
| **Storage** | 100 GB SSD untuk aplikasi + 500 GB storage untuk data |
| **Database** | MySQL 5.7+ dengan dedicated storage |
| **Cache** | Redis dedicated instance (4 GB RAM) |
| **Bandwidth** | Minimum 100 Mbps |
| **Redundancy** | SSD RAID 1 untuk high availability |
| **Backup** | Daily backup untuk disaster recovery |

#### **D. Network Requirements**

| Komponen | Requirement |
|----------|------------|
| **Client to Server** | HTTP/HTTPS connection |
| **WebSocket** | Port 80/443 (HTTP/HTTPS) |
| **Email Server** | SMTP server accessibility (port 587 or 25) |
| **Database** | Internal network connection |
| **File Storage** | Local filesystem or cloud storage API |
| **Load Balancer** | Optional untuk production scaling |

#### **E. Bandwidth Estimation**

| Operation | Data Size | Typical Bandwidth |
|-----------|-----------|------------------|
| Load homepage | ~500 KB | < 1 second (2 Mbps) |
| View product list | ~1-2 MB | 1-2 seconds (2 Mbps) |
| Add to cart | ~10 KB | Instant |
| Checkout process | ~50 KB | < 1 second |
| Image upload (foto) | 2-5 MB | 2-5 seconds (2 Mbps) |
| Download report | ~5 MB | 5-10 seconds (2 Mbps) |

**Estimated monthly bandwidth:** ~50-100 GB untuk UMKM dengan 500-1000 active users

---

### **3.3.5 Analisis Kebutuhan Infrastruktur (Infrastructure Requirements)**

#### **A. Development Environment Setup**

```
Developer Machine (Windows/Mac/Linux)
├── Python 3.8+ (virtual environment)
├── Django 4.2
├── SQLite3 database (local)
├── Daphne ASGI server
├── Redis (optional, untuk local testing)
└── Visual Studio Code + Extensions
```

#### **B. Production Environment (Recommended Stack)**

```
Load Balancer (Nginx)
└── Application Servers (Gunicorn, multiple instances)
    ├── Django 4.2 instances
    ├── Celery workers
    └── Daphne ASGI servers (for WebSocket)

Database Layer
├── MySQL 5.7+ (primary)
└── Redis (for caching & Celery broker)

File Storage
├── Local filesystem (for development)
└── AWS S3 / MinIO (for production)

Monitoring & Backup
├── Application logging (ELK stack or CloudWatch)
├── Database backups (daily)
└── Performance monitoring
```

#### **C. Security Requirements**

- **HTTPS/SSL:** Mandatory for production
- **Database encryption:** For sensitive data
- **Environment variables:** For secret keys and credentials
- **CORS configuration:** For API security
- **Rate limiting:** For DDoS protection
- **Firewall rules:** For network security

---

## 3.4 Perancangan Tabel Database

Perancangan tabel adalah proses mendefinisikan struktur dari masing-masing tabel dalam basis data, termasuk nama tabel, nama atribut (kolom), tipe data, panjang karakter, serta penetapan Primary key dan Foreign key. Tujuan dari perancangan ini adalah untuk mengatur data secara sistematis agar mudah diakses, dikelola, dan dikembangkan. Perancangan tabel yang baik akan menghasilkan database yang efisien, terstruktur, dan minim redundansi data. Setiap tabel mewakili satu entitas dalam sistem, dan kolom-kolomnya merepresentasikan atribut dari entitas tersebut.

Sistem UD. Barokah Jaya Beton menggunakan **8 tabel utama** dengan relasi yang terstruktur untuk mendukung semua fungsi bisnis. Berikut adalah perancangan lengkap setiap tabel:

---

### **3.4.1 Tabel Kategori**

Tabel Kategori dirancang sebagai struktur dasar untuk menyimpan dan mengelola kategori produk dalam basis data. Tabel ini menyediakan kategorisasi untuk memudahkan pelanggan dalam mencari produk yang mereka inginkan.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | nama_kategori | Varchar | 255 | Nama kategori produk |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key) dengan auto-increment untuk setiap kategori
- **nama_kategori:** Nama deskriptif kategori (misalnya: "Beton Cor", "Batu Bata", dll)

**Relasi:** One-to-Many dengan Tabel Produk

**Implementasi di Code:**
```python
class Kategori(models.Model):
    id = models.AutoField(primary_key=True)
    nama_kategori = models.CharField(max_length=255)
    class Meta:
        db_table = 'kategori'
```

---

### **3.4.2 Tabel Produk**

Tabel Produk dirancang untuk menyimpan data lengkap setiap produk yang ditawarkan oleh UD. Barokah Jaya Beton dengan rincian yang terstruktur.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | nama_produk | Varchar | 255 | Nama produk |
| 3 | deskripsi_produk | Text | - | Deskripsi detail produk |
| 4 | foto_produk | ImageField | - | Path/URL foto produk |
| 5 | stok_produk | Int | - | Jumlah stok tersedia |
| 6 | harga_produk | Decimal | 10,2 | Harga produk (Rp) |
| 7 | kategori_id | Int (FK) | - | Foreign Key ke Tabel Kategori |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key) dengan auto-increment
- **nama_produk:** Nama produk beton (misalnya: "Beton K-225 10x20")
- **deskripsi_produk:** Deskripsi lengkap spesifikasi produk
- **foto_produk:** File path untuk gambar produk (stored di `/media/produk_images/`)
- **stok_produk:** Integer untuk tracking inventory real-time
- **harga_produk:** Decimal precision 10,2 untuk akurasi harga
- **kategori_id:** Foreign Key untuk relasi One-to-Many dengan Kategori

**Relasi:** 
- One-to-Many dengan Tabel DetailTransaksi
- Many-to-One dengan Tabel Kategori
- One-to-Many dengan Tabel DiskonPelanggan

**Implementasi di Code:**
```python
class Produk(models.Model):
    id = models.AutoField(primary_key=True)
    nama_produk = models.CharField(max_length=255)
    deskripsi_produk = models.TextField()
    foto_produk = models.ImageField(upload_to='produk_images/')
    stok_produk = models.IntegerField()
    harga_produk = models.DecimalField(max_digits=10, decimal_places=2)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
    class Meta:
        db_table = 'produk'
```

---

### **3.4.3 Tabel Admin**

Tabel Admin dirancang untuk menyimpan data otentikasi dan identitas pengguna yang memiliki hak akses administratif sistem (pemilik usaha).

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | nama_lengkap | Varchar | 255 | Nama lengkap admin |
| 3 | username | Varchar | 150 | Username untuk login |
| 4 | password | Varchar | 128 | Password terenkripsi (hash) |
| 5 | email | EmailField | 254 | Email admin |
| 6 | is_staff | Boolean | - | Flag untuk akses admin Django |
| 7 | is_active | Boolean | - | Status aktif/tidak aktif |
| 8 | created_at | DateTime | - | Waktu pembuatan akun |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **nama_lengkap:** Nama lengkap administrator
- **username:** Username unik untuk login
- **password:** Password terenkripsi menggunakan Django's make_password()
- **email:** Email untuk notifikasi dan recovery
- **is_staff:** Flag Django untuk akses ke admin panel
- **is_active:** Status aktif/tidak aktif akun
- **created_at:** Timestamp pembuatan akun

**Security Notes:**
- Password disimpan dalam bentuk hash SHA-256, bukan plaintext
- Django's built-in authentication system digunakan
- Email unique untuk password recovery

**Implementasi di Code:**
```python
class Admin(AbstractUser):
    nama_lengkap = models.CharField(max_length=255)
    class Meta:
        db_table = 'admin'
```

---

### **3.4.4 Tabel Pelanggan**

Tabel Pelanggan dirancang untuk menyimpan data pengguna yang melakukan transaksi melalui sistem e-commerce. Tabel ini mendukung fungsionalitas CRM dan personalisasi layanan.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | nama_pelanggan | Varchar | 255 | Nama lengkap pelanggan |
| 3 | alamat | Text | - | Alamat tempat tinggal pelanggan |
| 4 | tanggal_lahir | Date | - | Tanggal lahir (untuk deteksi ulang tahun) |
| 5 | no_hp | Varchar | 20 | Nomor HP untuk kontak |
| 6 | username | Varchar | 150 | Username untuk login pelanggan |
| 7 | password | Varchar | 128 | Password terenkripsi |
| 8 | email | EmailField | 254 | Email pelanggan (unik) |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **nama_pelanggan:** Nama lengkap pelanggan
- **alamat:** Alamat pengiriman default
- **tanggal_lahir:** Digunakan untuk fitur birthday discount otomatis
- **no_hp:** Nomor HP untuk komunikasi
- **username:** Username unik untuk login
- **password:** Password terenkripsi
- **email:** Email unik dengan notifikasi

**CRM Features:**
- Deteksi ulang tahun otomatis untuk trigger diskon P2-A/P2-B
- Tracking riwayat transaksi melalui Foreign Key
- Email notification untuk event penting

**Relasi:** One-to-Many dengan Tabel Transaksi, DiskonPelanggan, Notifikasi

**Implementasi di Code:**
```python
class Pelanggan(models.Model):
    id = models.AutoField(primary_key=True)
    nama_pelanggan = models.CharField(max_length=255)
    alamat = models.TextField()
    tanggal_lahir = models.DateField()
    no_hp = models.CharField(max_length=20)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=254, unique=True, null=True)
    class Meta:
        db_table = 'pelanggan'
```

---

### **3.4.5 Tabel Transaksi**

Tabel Transaksi dirancang secara komprehensif untuk merekam detail dari setiap proses pembelian, termasuk informasi pembayaran, pengiriman, dan feedback.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | tanggal | DateTime | - | Waktu transaksi dibuat |
| 3 | total | Decimal | 10,2 | Total harga transaksi (Rp) |
| 4 | ongkir | Decimal | 10,2 | Biaya pengiriman (Rp) |
| 5 | status_transaksi | Varchar | 50 | Status pesanan |
| 6 | bukti_bayar | FileField | - | File bukti pembayaran upload |
| 7 | alamat_pengiriman | Text | - | Alamat pengiriman detail |
| 8 | feedback | Text | - | Feedback pelanggan setelah pesanan selesai |
| 9 | fotofeedback | ImageField | - | Foto feedback pelanggan |
| 10 | waktu_checkout | DateTime | - | Waktu checkout (reference untuk deadline) |
| 11 | batas_waktu_bayar | DateTime | - | Deadline pembayaran (checkout + 24 jam) |
| 12 | foto_pengiriman | ImageField | - | Foto verifikasi pengiriman oleh karyawan |
| 13 | idPelanggan | Int (FK) | - | Foreign Key ke Tabel Pelanggan |

**Status Choices:**
- `DIPROSES` - Pesanan baru, menunggu pembayaran
- `DIBAYAR` - Pembayaran telah diterima & diverifikasi admin
- `DIKIRIM` - Pesanan dalam proses pengiriman
- `SELESAI` - Pesanan sudah diterima pelanggan
- `DIBATALKAN` - Pesanan dibatalkan

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **tanggal:** Timestamp pembuatan transaksi
- **total:** Decimal precision 10,2 untuk akurasi (Rp)
- **ongkir:** Biaya pengiriman (default 0 untuk pickup)
- **status_transaksi:** Current status dalam workflow
- **bukti_bayar:** File path bukti transfer (stored di `/media/bukti_pembayaran/`)
- **alamat_pengiriman:** Alamat spesifik untuk pengiriman ini
- **feedback:** Text feedback pelanggan (untuk quality improvement)
- **fotofeedback:** Foto bukti untuk feedback (stored di `/media/feedback_images/`)
- **waktu_checkout:** Checkpoint untuk payment deadline calculation
- **batas_waktu_bayar:** Auto-calculated 24 jam setelah checkout
- **foto_pengiriman:** Bukti foto pengiriman oleh karyawan (stored di `/media/verifikasi_pengiriman/`)
- **idPelanggan:** Foreign Key ke Pelanggan

**Business Logic:**
- 24-hour payment window: `batas_waktu_bayar = waktu_checkout + 24 hours`
- Atomic transaction pada `proses_pembayaran()` untuk consistency
- Status workflow: DIPROSES → DIBAYAR → DIKIRIM → SELESAI

**Relasi:** One-to-Many dengan Tabel DetailTransaksi

**Implementasi di Code:**
```python
class Transaksi(models.Model):
    id = models.AutoField(primary_key=True)
    tanggal = models.DateTimeField(default=date.today)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ongkir = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status_transaksi = models.CharField(max_length=50, choices=STATUS_TRANSAKSI_CHOICES, default='DIPROSES')
    bukti_bayar = models.FileField(upload_to='bukti_pembayaran/', null=True)
    alamat_pengiriman = models.TextField(null=True)
    feedback = models.TextField(null=True)
    fotofeedback = models.ImageField(upload_to='feedback_images/', null=True)
    foto_pengiriman = models.ImageField(upload_to='verifikasi_pengiriman/', null=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'transaksi'
```

---

### **3.4.6 Tabel DetailTransaksi**

Tabel DetailTransaksi dirancang sebagai junction table (tabel penghubung) antara transaksi utama dan produk yang dibeli, untuk mendukung many-to-many relationship.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | jumlah_produk | Int | - | Quantity produk yang dibeli |
| 3 | sub_total | Decimal | 10,2 | Total harga per item (qty × price) |
| 4 | idProduk | Int (FK) | - | Foreign Key ke Tabel Produk |
| 5 | idTransaksi | Int (FK) | - | Foreign Key ke Tabel Transaksi |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **jumlah_produk:** Quantity dari produk ini dalam transaksi
- **sub_total:** Total untuk item ini (Rp) = jumlah_produk × harga_produk
- **idProduk:** Foreign Key ke Produk
- **idTransaksi:** Foreign Key ke Transaksi

**Business Logic:**
- Setiap transaksi dapat memiliki multiple DetailTransaksi (many-to-many melalui junction table)
- `sub_total` dihitung: `jumlah_produk × Produk.harga_produk`
- Total transaksi = SUM(DetailTransaksi.sub_total) + Transaksi.ongkir

**Relasi:** 
- Many-to-One dengan Tabel Transaksi
- Many-to-One dengan Tabel Produk

**Implementasi di Code:**
```python
class DetailTransaksi(models.Model):
    id = models.AutoField(primary_key=True)
    jumlah_produk = models.IntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    idTransaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE)
    class Meta:
        db_table = 'detail_transaksi'
```

---

### **3.4.7 Tabel DiskonPelanggan**

Tabel DiskonPelanggan dirancang untuk mengelola sistem diskon berlapis yang sophisticated, dengan mendukung multiple scope dan priority tiers.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | persen_diskon | Int | - | Persentase diskon (0-100) |
| 3 | status | Varchar | 50 | Status diskon (aktif/tidak_aktif) |
| 4 | pesan | Text | - | Deskripsi atau catatan diskon |
| 5 | tanggal_dibuat | DateTime | - | Waktu pembuatan diskon |
| 6 | berlaku_sampai | DateTime | - | Expiry date diskon |
| 7 | scope_diskon | Varchar | 50 | Scope: SINGLE_PRODUCT / ALL_PRODUCTS / CART_THRESHOLD |
| 8 | minimum_cart_total | Decimal | 10,2 | Minimum cart amount untuk threshold discount |
| 9 | idProduk | Int (FK) | - | Foreign Key ke Produk (NULL jika ALL_PRODUCTS) |
| 10 | idPelanggan | Int (FK) | - | Foreign Key ke Pelanggan |

**Status Choices:**
- `aktif` - Diskon sedang berlaku
- `tidak_aktif` - Diskon tidak aktif

**Scope Choices:**
- `SINGLE_PRODUCT` - Diskon untuk satu produk spesifik
- `ALL_PRODUCTS` - Diskon untuk semua produk (Loyalitas P2-A)
- `CART_THRESHOLD` - Diskon jika cart ≥ minimum_cart_total (Birthday P2-B)

**Priority Tier System:**
1. **P1 (Manual Single-Product):** `idProduk` ≠ NULL, `scope_diskon = SINGLE_PRODUCT`
2. **P2 (Manual General):** `idProduk = NULL`, `scope_diskon = ALL_PRODUCTS`
3. **P2-A (Loyalty):** `scope_diskon = ALL_PRODUCTS`, minimum cart ≥ Rp 5,000,000
4. **P2-B (Birthday):** `scope_diskon = CART_THRESHOLD`, triggered saat ulang tahun

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **persen_diskon:** Persentase diskon (integer 0-100)
- **status:** Flag aktif/tidak aktif untuk easy enable/disable
- **pesan:** Deskripsi diskon (untuk admin notes)
- **tanggal_dibuat:** Auto timestamp
- **berlaku_sampai:** Expiry date untuk limited-time promotions
- **scope_diskon:** Determines how discount is applied
- **minimum_cart_total:** For CART_THRESHOLD scope, minimum cart value required
- **idProduk:** NULL untuk ALL_PRODUCTS atau CART_THRESHOLD, filled untuk SINGLE_PRODUCT
- **idPelanggan:** Target pelanggan

**Application Logic:**
- Diskon di-apply otomatis di `proses_pembayaran()` dengan priority checking
- Multiple diskon dengan priority hierarchy
- Calculation: `final_price = price × (1 - diskon_persen/100)`

**Relasi:** Many-to-One dengan Tabel Pelanggan dan Produk

**Implementasi di Code:**
```python
class DiskonPelanggan(models.Model):
    id = models.AutoField(primary_key=True)
    persen_diskon = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_DISKON_CHOICES, default='aktif')
    pesan = models.TextField(null=True)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    berlaku_sampai = models.DateTimeField(null=True)
    scope_diskon = models.CharField(max_length=50, choices=SCOPE_DISKON_CHOICES, default='SINGLE_PRODUCT')
    minimum_cart_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    idProduk = models.ForeignKey(Produk, on_delete=models.CASCADE, null=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'diskon_pelanggan'
```

---

### **3.4.8 Tabel Notifikasi**

Tabel Notifikasi dirancang untuk merekam dan mengelola semua pemberitahuan yang dikirimkan kepada pelanggan, mendukung both in-app dan email notifications.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | tipe_pesan | Varchar | 50 | Tipe notifikasi (payment, shipment, birthday, etc) |
| 3 | isi_pesan | Text | - | Konten detail notifikasi |
| 4 | is_read | Boolean | - | Status read/unread |
| 5 | created_at | DateTime | - | Waktu notifikasi dibuat |
| 6 | link_cta | Varchar | 255 | Call-to-Action URL link |
| 7 | idPelanggan | Int (FK) | - | Foreign Key ke Pelanggan |

**Tipe Pesan:**
- `payment_approved` - Pembayaran telah diapprove admin
- `order_shipped` - Pesanan sedang dalam perjalanan
- `order_completed` - Pesanan selesai diterima
- `birthday_promo` - Notifikasi diskon ulang tahun
- `new_product` - Notifikasi produk baru
- `stock_alert` - Alert stok terbatas

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **tipe_pesan:** Kategori notifikasi untuk filtering dan template
- **isi_pesan:** Content lengkap notifikasi (bisa HTML)
- **is_read:** Boolean flag untuk mark as read functionality
- **created_at:** Auto timestamp notification creation
- **link_cta:** URL untuk action button di notifikasi (optional)
- **idPelanggan:** Foreign Key ke Pelanggan (recipient)

**Real-Time Features:**
- Notifikasi dikirim via WebSocket (Channels/Daphne) untuk in-app delivery
- Background task via Celery untuk email notifications
- Stored di database untuk notification center

**Notification Flow:**
1. Event triggered (e.g., payment approved)
2. `send_notification_task()` Celery task created
3. In-app notification sent via WebSocket
4. Email notification sent via SMTP
5. Record stored di Notifikasi table
6. Pelanggan lihat di notification center

**Relasi:** Many-to-One dengan Tabel Pelanggan

**Implementasi di Code:**
```python
class Notifikasi(models.Model):
    id = models.AutoField(primary_key=True)
    tipe_pesan = models.CharField(max_length=50)
    isi_pesan = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link_cta = models.CharField(max_length=255, null=True)
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'notifikasi'
```

---

### **3.4.9 Tabel Karyawan (Employee Delivery Staff)**

Tabel Karyawan dirancang untuk mengelola data karyawan yang bertanggung jawab dalam proses verifikasi dan pengiriman pesanan.

| No. | Field | Type | Length | Keterangan |
|-----|-------|------|--------|-----------|
| 1 | id | Int (AutoField) | - | Primary Key, auto increment |
| 2 | nama | Varchar | 255 | Nama karyawan |
| 3 | email | EmailField | 254 | Email karyawan (unik) |
| 4 | password | Varchar | 128 | Password terenkripsi |
| 5 | is_active | Boolean | - | Status aktif/tidak aktif |
| 6 | created_at | DateTime | - | Waktu account dibuat |

**Deskripsi:**
- **id:** Pengenal unik (Primary Key)
- **nama:** Nama lengkap karyawan
- **email:** Email unik untuk login
- **password:** Password terenkripsi (hashed)
- **is_active:** Flag aktif/tidak aktif (untuk disable account)
- **created_at:** Timestamp account creation

**Authentication:**
- Separate session-based authentication dari Pelanggan dan Admin
- Session key: `karyawan_id` (berbeda dari `pelanggan_id` dan `user_id`)
- Decorated views dengan `@karyawan_required` untuk role-based access

**Features:**
- Dashboard khusus karyawan untuk lihat pesanan DIKIRIM
- Form verifikasi pengiriman dengan upload foto
- Upload foto ke `/media/verifikasi_pengiriman/`

**Relasi:** One-to-Many dengan Transaksi (implicit melalui delivery verification process)

**Implementasi di Code:**
```python
class Karyawan(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    class Meta:
        db_table = 'karyawan'
```

---

## 3.5 Database Relationships (Entity Relationship Diagram - Konseptual)

Berikut adalah relasi antar tabel yang telah dirancang:

```
┌─────────────┐
│  Kategori   │
│  (1)        │
└──────┬──────┘
       │ (1:M)
       │
       ▼
┌─────────────────────┐
│   Produk            │────────┐
│   (M)               │        │
└──────┬──────────────┘        │
       │ (1:M)                 │ (1:M)
       │                       │
       ▼                       ▼
┌──────────────────────────────────────────────────────────────┐
│   DetailTransaksi  (Junction Table)                         │
│   - idTransaksi (FK) ─────────┐                             │
│   - idProduk (FK) ────────────┴─ (Mengumpulkan semua)      │
└──────────────────────────────────────────────────────────────┘
       △                       △
       │ (1:M)                 │ (1:M)
       │                       │
       └───────────────────────┤
                               │
┌──────────────────┐           │
│  Transaksi       │◄──────────┘
│                  │
│  - idPelanggan   │ (1:M)
│    (FK)          │
└────────┬─────────┘
         │
         │ (M:1)
         │
         ▼
┌──────────────────────┐
│  Pelanggan           │
│                      │
│  (Hub untuk CRM)     │◄────────────────┐
└────────┬─────────────┘                 │
         │                              │
         │ (1:M)                        │ (M:1)
         │                              │
         ├──────────┐          ┌────────┤
         │          │          │        │
         ▼          ▼          ▼        │
    Notifikasi  DiskonPelanggan ────────┘
                   + Produk (FK)
```

**Relationship Summary:**

| Relasi | From | To | Type | Deskripsi |
|--------|------|----|----|-----------|
| 1 | Kategori | Produk | 1:M | Satu kategori memiliki banyak produk |
| 2 | Produk | DetailTransaksi | 1:M | Satu produk dapat ada di banyak transaksi |
| 3 | Transaksi | DetailTransaksi | 1:M | Satu transaksi memiliki banyak detail item |
| 4 | Pelanggan | Transaksi | 1:M | Satu pelanggan melakukan banyak transaksi |
| 5 | Pelanggan | DiskonPelanggan | 1:M | Satu pelanggan dapat menerima banyak diskon |
| 6 | Produk | DiskonPelanggan | 1:M | Satu produk dapat memiliki banyak diskon |
| 7 | Pelanggan | Notifikasi | 1:M | Satu pelanggan menerima banyak notifikasi |
| 8 | Admin | - | - | Independent, manages system |
| 9 | Karyawan | - | - | Independent, handles delivery |

---

## 3.6 Ringkasan Kebutuhan Sistem

Berdasarkan analisis di atas, sistem membutuhkan:

1. **Functional Requirements:** 10 kategori fungsi dengan 50+ sub-fungsi
2. **User Roles:** 3 peran (Admin, Pelanggan, Karyawan) dengan hak akses berbeda
3. **Technology Stack:** Modern Web development stack dengan real-time capability
4. **Hardware:** Light requirement untuk client (4GB RAM), moderate untuk server (8-16GB)
5. **Network:** Minimum 2 Mbps untuk client, 100 Mbps for server
6. **Infrastructure:** Cloud atau on-premise dengan proper backup & monitoring
7. **Database Schema:** 9 tabel dengan proper relationships dan constraints
8. **Data Integrity:** Atomic transactions, Foreign Keys, dan validation rules

Semua kebutuhan di atas telah dipertimbangkan dan diimplementasikan dalam design dan implementation sistem UD. Barokah Jaya Beton.

