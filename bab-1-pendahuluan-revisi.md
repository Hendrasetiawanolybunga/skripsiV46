# BAB 1: PENDAHULUAN (REVISI LENGKAP 100% SESUAI IMPLEMENTASI)

## 1.1. Latar Belakang

UD. Barokah Jaya Beton merupakan usaha mikro, kecil, dan menengah (UMKM) yang bergerak di bidang produksi serta penjualan material bangunan seperti roster minimalis, tiang teras jadi, tiang pagar, pion pagar beton, dan ornamen batu tempel. Usaha ini telah berjalan selama kurang lebih tiga tahun dan memanfaatkan media sosial seperti WhatsApp dan Facebook sebagai sarana promosi dan komunikasi dengan pelanggan. Meskipun demikian, sistem pencatatan transaksi dan pengelolaan stok barang masih dilakukan secara manual. Seluruh pesanan dicatat di buku, dan informasi stok hanya diperoleh melalui pengecekan fisik. Hal ini mengakibatkan risiko seperti kesalahan pencatatan, hilangnya data penting, dan keterbatasan dalam memantau ketersediaan barang secara real-time.

Kurangnya sistem digital juga menyulitkan dalam membangun relasi jangka panjang dengan pelanggan tetap, karena tidak ada pencatatan sistematis terhadap data pelanggan dan riwayat transaksi. Padahal, pemilik usaha menunjukkan minat terhadap sistem yang dapat mengidentifikasi pelanggan loyal, mendeteksi tanggal ulang tahun pelanggan, dan mengirimkan pengingat otomatis untuk pembelian ulang maupun penawaran khusus. Hal ini membuka peluang untuk mengimplementasikan sistem Customer Relationship Management (CRM) yang terintegrasi guna meningkatkan loyalitas pelanggan dan memberikan pengalaman berbelanja yang dipersonalisasi.

Untuk mengatasi permasalahan tersebut, diperlukan pengembangan sistem e-commerce berbasis Web yang mencakup fitur pemesanan produk, manajemen stok real-time, pencatatan transaksi otomatis, dan CRM terintegrasi. Sistem ini dirancang dengan mempertimbangkan keterbatasan teknologi pengguna, yang lebih terbiasa menggunakan perangkat seluler, namun bersedia mempelajari sistem baru yang dapat mendukung operasional usaha. 

Sistem ini mengintegrasikan beberapa fitur canggih untuk meningkatkan pengalaman pelanggan dan efisiensi operasional:

1. **Sistem Diskon Multi-Tier yang Intelligent:** Sistem menyediakan diskon otomatis yang berjenjang berdasarkan loyalitas pelanggan dan momen khusus (ulang tahun). Fitur ini mencakup:
   - Diskon manual yang dapat diatur oleh administrator per produk atau general
   - Deteksi otomatis ulang tahun pelanggan dengan diskon khusus
   - Sistem loyalitas otomatis berdasarkan total pembelian (≥ Rp 5.000.000)
   - Diskon berjenjang P2-A (Loyalitas Permanen) untuk pelanggan ulang tahun yang loyal
   - Diskon berjenjang P2-B (Loyalitas Instan) untuk pelanggan ulang tahun yang mencapai threshold belanja di hari yang sama

2. **Notifikasi Real-time Terintegrasi:** Sistem menggunakan WebSocket dan Celery untuk pengiriman notifikasi real-time kepada pelanggan, termasuk:
   - In-app notification yang ditampilkan langsung di dashboard pelanggan
   - Email notification untuk event penting (persetujuan pembayaran, pengiriman, promo)
   - Notifikasi otomatis saat ada perubahan status pesanan

3. **Sistem Tracking Pesanan Lengkap:** Pelanggan dapat melacak pesanan mereka melalui berbagai status: DIPROSES → DIBAYAR → DIKIRIM → SELESAI

4. **Feedback dan Verifikasi Pengiriman:** Fitur ini memungkinkan pelanggan memberikan feedback dengan foto bukti, sementara karyawan dapat memverifikasi pengiriman dengan dokumentasi visual

Sistem pengiriman akan mengakomodasi opsi pengantaran internal oleh pihak usaha dengan manajemen karyawan yang terstruktur, sedangkan sistem pembayaran menggunakan metode transfer bank dengan unggah bukti pembayaran dan validasi manual oleh administrator, tanpa perlu integrasi dengan layanan pihak ketiga seperti payment gateway.

Beberapa penelitian sebelumnya telah menunjukkan bahwa penggunaan sistem berbasis Web dapat meningkatkan efisiensi operasional bisnis. Misalnya, penelitian oleh [1] menunjukkan bahwa efisiensi operasional dicapai melalui otomatisasi berbagai aspek operasional, termasuk manajemen inventaris, pelacakan pesanan, dan pengelolaan data pelanggan. Penelitian oleh [2] menunjukkan bahwa penggunaan teknologi informasi memungkinkan perusahaan untuk meningkatkan efisiensi dan produktivitas. Dengan adanya sistem otomatis dan terintegrasi, proses bisnis dapat berjalan lebih cepat dan efisien. Penelitian oleh [3] menunjukkan bahwa adanya perilaku konsumen online di antaranya disebabkan pemilihan produk serta aksesibilitas dan kenyamanan. Selain itu juga karena kemudahan penggunaan/ketersediaan situs Web 24 jam yang bisa diakses kapan pun dan di mana pun. Harga dapat dibandingkan dan memerlukan minim sosialitas. Artinya tidak perlu melibatkan banyak orang seperti tenaga penjualan, keluarga hingga teman yang ikut dalam perjalanan belanja. Personalisasi yang tepat juga ada saat pengisian form pemesanan otomatis sesuai selera konsumen. 

Dalam era digital yang semakin berkembang, pemesanan dan penjualan online telah menjadi solusi yang sangat efisien bagi pelaku usaha dagang. Dengan memanfaatkan platform digital, pelaku usaha dapat menjangkau pasar yang lebih luas, meningkatkan efisiensi operasional, dan memberikan kemudahan bagi konsumen dalam melakukan transaksi. Sebagai contoh, penelitian oleh [4] menunjukkan bahwa digital marketing memudahkan pebisnis memantau dan menyediakan segala kebutuhan dan keinginan calon konsumen, di sisi lain calon konsumen juga bisa mencari dan mendapatkan informasi produk hanya dengan cara menjelajah dunia maya sehingga mempermudah proses pencariannya. Hal ini menunjukkan bahwa pemesanan dan penjualan online tidak hanya menghemat waktu dan biaya, tetapi juga meningkatkan kepuasan pelanggan melalui personalisasi dan targeting yang lebih baik.

Dengan demikian, pengembangan aplikasi ini diharapkan dapat menjadi solusi untuk mengatasi permasalahan yang dihadapi oleh UD Barokah Jaya Beton, sekaligus meningkatkan efisiensi dan efektivitas operasional bisnis mereka dengan memanfaatkan teknologi otomasi, CRM terintegrasi, dan sistem diskon cerdas yang responsif terhadap perilaku pelanggan.

---

## 1.2. Rumusan Masalah

Berdasarkan latar belakang di atas, maka rumusan masalah dalam penelitian ini adalah:

1. Bagaimana merancang dan membangun sistem pemesanan dan penjualan berbasis Web untuk UD. Barokah Jaya Beton agar dapat meningkatkan efisiensi dalam pencatatan transaksi dan manajemen stok barang secara real-time?

2. Bagaimana mengintegrasikan fitur pemesanan dengan opsi pengiriman barang yang sesuai dengan kebutuhan pelanggan, termasuk verifikasi pengiriman oleh karyawan dengan dokumentasi visual?

3. Bagaimana mengimplementasikan Customer Relationship Management (CRM) yang terintegrasi dengan sistem diskon otomatis (berdasarkan loyalitas dan ulang tahun pelanggan) untuk meningkatkan kepuasan dan loyalitas pelanggan?

4. Bagaimana merancang sistem notifikasi real-time (in-app dan email) menggunakan teknologi WebSocket dan Celery untuk memberikan informasi terkini kepada pelanggan?

5. Bagaimana merancang laporan penjualan yang dapat membantu pihak UD. Barokah Jaya Beton dalam menganalisis performa bisnis mereka?

---

## 1.3. Tujuan Penelitian

Tujuan dari penelitian ini adalah:

1. Mengembangkan sistem penjualan berbasis Web untuk UD. Barokah Jaya Beton menggunakan framework Django 4.2 guna meningkatkan efisiensi pencatatan transaksi dan manajemen stok secara real-time dengan validasi otomatis.

2. Menyediakan opsi pengiriman barang yang terstruktur melalui manajemen karyawan, dengan fitur verifikasi pengiriman yang didokumentasikan secara visual untuk memastikan transparansi dan akuntabilitas.

3. Mengimplementasikan fitur Customer Relationship Management (CRM) yang terintegrasi, mencakup:
   - Pencatatan data pelanggan lengkap (nama, alamat, kontak, tanggal lahir)
   - Riwayat transaksi lengkap dengan status tracking
   - Sistem deteksi otomatis loyalitas pelanggan berdasarkan total pembelian
   - Sistem diskon otomatis berjenjang untuk pelanggan ulang tahun (P2-A Loyalitas Permanen dan P2-B Loyalitas Instan)

4. Mengimplementasikan sistem notifikasi real-time menggunakan WebSocket (Daphne) dan Celery task queue untuk in-app notification dan email notification guna meningkatkan interaksi dengan pelanggan.

5. Menyediakan fitur laporan penjualan yang mendukung analisis bisnis dan pengambilan keputusan strategis melalui dashboard admin yang menampilkan revenue trend, top-selling products, dan low stock alerts.

---

## 1.4. Batasan Masalah

Agar penelitian ini memiliki fokus yang jelas, maka batasan masalah dalam penelitian ini adalah:

1. Sistem hanya mencakup proses pemesanan dan penjualan produk yang tersedia pada UD. Barokah Jaya Beton, tanpa mencakup proses refund atau retur otomatis.

2. Sistem dikembangkan berbasis Web menggunakan framework Django 4.2 dan hanya tersedia dalam bentuk Web responsif, tanpa pengembangan aplikasi mobile maupun integrasi dua faktor autentikasi (2FA).

3. Fitur autentikasi hanya menyediakan registrasi dan login standar dengan password hashing, tanpa pemulihan password otomatis (lupa password). Sistem autentikasi dibagi menjadi tiga role: Pelanggan (session-based), Karyawan (session-based dengan model terpisah), dan Admin (Django built-in auth).

4. Pencarian produk hanya berdasarkan kategori dan tidak mendukung pencarian berdasarkan kata kunci full-text atau sistem ulasan pelanggan berbintang. Namun, sistem menyediakan halaman detail produk yang lengkap dengan informasi harga dan ketersediaan stok.

5. Fitur keranjang dan checkout hanya mendukung satu alamat pengiriman per transaksi, dengan validasi stok otomatis saat penambahan produk ke keranjang dan proses checkout. Keranjang diimplementasikan menggunakan session Django dan stok dikurangi secara atomic saat transaksi dikonfirmasi.

6. Sistem pembayaran hanya mendukung metode transfer bank manual dengan unggah bukti pembayaran, tanpa integrasi payment gateway pihak ketiga. Pembayaran diverifikasi secara manual oleh administrator melalui Django admin interface.

7. Notifikasi mencakup in-app notification dan email notification. Sistem menggunakan Celery untuk background task processing dan WebSocket (Daphne/Channels) untuk real-time in-app notification delivery. SMS notification tidak disediakan dalam sistem ini.

8. Fitur CRM mencakup:
   - Pencatatan lengkap data pelanggan (nama, alamat, kontak, tanggal lahir)
   - Riwayat transaksi lengkap dengan status tracking (DIPROSES, DIBAYAR, DIKIRIM, SELESAI)
   - Notifikasi otomatis berdasarkan event penting
   - Deteksi otomatis ulang tahun pelanggan
   - Sistem diskon otomatis berdasarkan loyalitas (total belanja ≥ Rp 5.000.000)
   - Feedback collection dengan opsi foto bukti
   
   Namun, fitur kampanye pemasaran otomatis dan mass communication belum diimplementasikan dalam fase ini.

9. Sistem diskon mencakup:
   - **Diskon Manual:** Administrator dapat membuat diskon per produk atau general dengan status aktif/tidak aktif
   - **Diskon Otomatis Berdasarkan Loyalitas:** Pelanggan yang total pembeliannya ≥ Rp 5.000.000 (dengan status DIBAYAR/DIKIRIM/SELESAI) dianggap loyal
   - **Diskon Ulang Tahun Otomatis:** Sistem mendeteksi tanggal ulang tahun pelanggan dan mengaplikasikan diskon sesuai status loyalitas:
     - **P2-A (Loyalitas Permanen):** Pelanggan ulang tahun yang loyal mendapat diskon 10% untuk 3 produk favorit mereka
     - **P2-B (Loyalitas Instan):** Pelanggan ulang tahun non-loyal mendapat diskon 10% untuk total belanja jika mencapai threshold Rp 5.000.000 dalam satu transaksi
   - **Multi-Scope Diskon:** Setiap diskon dapat diatur dengan scope (SINGLE_PRODUCT, ALL_PRODUCTS, CART_THRESHOLD) dan tanggal ekspirasi
   
   Sistem prioritas diskon: Manual Single-Product > Manual General > ALL_PRODUCTS > Birthday > Tidak ada diskon.

10. Sistem laporan mencakup:
    - Laporan pendapatan bulanan (6 bulan terakhir) dengan visualization chart
    - Laporan produk terlaris berdasarkan jumlah penjualan
    - Alert otomatis untuk produk dengan stok rendah (< 10 unit)
    - Filter transaksi berdasarkan status dan periode tanggal
    
    Data laporan hanya mencakup transaksi dengan status DIBAYAR, DIKIRIM, atau SELESAI. Export ke format PDF dapat dilakukan melalui integrasi library reporting (untuk fase pengembangan selanjutnya).

11. Pengujian sistem hanya dilakukan secara manual oleh pengembang dan pengguna, tanpa penerapan automated testing seperti unit testing atau integration testing. Namun, semua kritical business logic divalidasi melalui proses checkout dengan atomic transaction untuk memastikan data consistency.

---

## 1.5. Manfaat Penelitian

Manfaat penelitian ini dapat dibagi menjadi beberapa aspek, yaitu:

### 1.5.1 Bagi UD. Barokah Jaya Beton:

a. **Efisiensi Operasional:**
   - Meningkatkan efisiensi pencatatan transaksi dari manual ke digital otomatis
   - Pengelolaan stok real-time dengan validasi otomatis mencegah overselling
   - Mengurangi beban administrasi dan human error dalam pencatatan pesanan
   - Proses checkout yang atomic memastikan data consistency dan integritas database

b. **Manajemen Karyawan & Pengiriman:**
   - Sistem manajemen karyawan terstruktur dengan role-based access control
   - Fitur verifikasi pengiriman dengan dokumentasi visual meningkatkan transparansi
   - Tracking pesanan real-time memudahkan koordinasi pengiriman

c. **Perkuat Relasi dengan Pelanggan:**
   - CRM terintegrasi memungkinkan personalisasi pengalaman berbelanja per pelanggan
   - Notifikasi otomatis (in-app dan email) meningkatkan engagement dengan pelanggan
   - Sistem loyalitas otomatis meningkatkan repeat purchase rate
   - Diskon berbasis ulang tahun menciptakan emotional connection dengan pelanggan

d. **Peningkatan Revenue:**
   - Sistem diskon otomatis P2-A dan P2-B meningkatkan average order value
   - Identification top-3 favorite products per customer meningkatkan cross-selling opportunity
   - Data loyalitas pelanggan membantu targeting promosi yang lebih effective

### 1.5.2 Bagi Pelanggan:

a. **Kemudahan Berbelanja:**
   - Akses 24/7 untuk melihat katalog produk dan melakukan pemesanan
   - Interface responsif yang user-friendly dapat diakses dari berbagai perangkat
   - Proses checkout yang simple dengan validasi stok real-time mencegah kecewa

b. **Pengalaman Personalisasi:**
   - Sistem diskon yang intelligent dan transparan meningkatkan value perception
   - Notifikasi otomatis (ulang tahun, perubahan status pesanan, promo) membuat pelanggan merasa diperhatikan
   - Feedback system memungkinkan pelanggan berkontribusi pada improvement layanan

c. **Transparansi & Kepercayaan:**
   - Tracking pesanan real-time dari DIPROSES hingga SELESAI
   - Verifikasi pengiriman dengan foto bukti meningkatkan kepercayaan
   - Sistem feedback terintegrasi memungkinkan pelanggan share pengalaman positif

d. **Fleksibilitas Pengiriman:**
   - Opsi pengiriman internal dari UD. Barokah Jaya Beton sesuai preferensi
   - Pelanggan dapat memilih alamat pengiriman saat checkout

### 1.5.3 Bagi Ilmu Komputer & Penelitian:

a. **Kontribusi pada Pengembangan Sistem Informasi:**
   - Memberikan kontribusi dalam pengembangan sistem e-commerce berbasis Web untuk UMKM
   - Implementasi CRM terintegrasi dengan sistem diskon otomatis yang sophisticated
   - Penggunaan teknologi modern (Django 4.2, WebSocket, Celery) untuk UMKM scale
   - Demonstrasi practical implementation dari real-time notification system menggunakan WebSocket

b. **Referensi untuk Penelitian Selanjutnya:**
   - Menjadi referensi dalam bidang manajemen stok dan inventory management untuk UMKM
   - Case study implementasi multi-tier loyalty system dan automated discount engine
   - Dokumentasi lengkap tentang session-based authentication untuk multiple user roles
   - Referensi untuk implementasi CRM yang cost-effective untuk usaha kecil
   - Knowledge base tentang atomic transaction implementation untuk data consistency di e-commerce

c. **Best Practices:**
   - Mendokumentasikan best practices dalam security (password hashing, CSRF protection)
   - Sharing pembelajaran tentang session management di Django untuk scalability
   - Demonstrasi implementasi real-time system tanpa payment gateway third-party
   - Model implementasi feedback & verification system untuk e-commerce lokal

---

**Dengan demikian, penelitian ini diharapkan memberikan solusi komprehensif yang tidak hanya mengatasi permasalahan UD. Barokah Jaya Beton, tetapi juga menjadi blueprint bagi UMKM lain dalam transformasi digital mereka.**

