# 🧱 Sistem Informasi Penjualan Online dan CRM Sederhana UD. Barokah Jaya Beton

Proyek ini adalah Sistem Informasi Penjualan dan CRM berbasis **Django** yang memanfaatkan **Celery** dan **Redis** untuk menangani proses asinkron (Notifikasi Real-time, Diskon Otomatis, dan Tugas Terjadwal).

## 🚀 PENGATURAN LINGKUNGAN (Development Setup)

Aplikasi ini memerlukan **empat layanan terpisah** untuk beroperasi penuh. Anda perlu membuka empat terminal berbeda.

### ✅ Prasyarat

Sebelum memulai, pastikan:

1.  **Redis Server** harus sudah berjalan di *background* (port default: `6379`).
2.  Anda telah mengaktifkan **Virtual Environment** (`source env/bin/activate`).

---

## 🖥️ PANDUAN EKSEKUSI 4 TERMINAL

Setiap terminal memiliki peran penting dalam arsitektur aplikasi:

### 1. Terminal 1: 🌐 ASGI Server (Daphne)

> **Peran:** Menangani semua koneksi **WebSocket** (Notifikasi) dan berfungsi sebagai *entry point* utama HTTP.

| Layanan | Perintah | Catatan |
| :--- | :--- | :--- |
| **Daphne** | `daphne ProyekBarokah.asgi:application -b 127.0.0.1 -p 8000` | Akses aplikasi utama di **http://127.0.0.1:8000/** |

### 2. Terminal 2: ⚙️ Celery Worker (Pemroses Utama)

> **Peran:** Mengeksekusi tugas-tugas yang dikirim ke antrian secara umum dan asinkron (misalnya, Notifikasi Transaksi, Diskon Manual Admin).

| Layanan | Perintah | Status |
| :--- | :--- | :--- |
| **Worker** | `celery -A ProyekBarokah worker --loglevel=info -P solo` | Siap memproses tugas |

### 3. Terminal 3: ⏱️ Celery Beat (Penjadwal Tugas)

> **Peran:** Bertindak sebagai *Cron Job* yang secara berkala **memicu tugas-tugas terjadwal** (misalnya, `check_birthday_and_loyalty_task`).

| Layanan | Perintah | Status |
| :--- | :--- | :--- |
| **Beat** | `celery -A ProyekBarokah beat -l info` | Memicu Diskon Otomatis (Ultah/Loyalitas) |

### 4. Terminal 4: 💻 Django Runserver (HTTP Development)

> **Peran:** Melayani permintaan HTTP biasa. Digunakan sebagai *fallback* atau *development* server terpisah.

| Layanan | Perintah | Status |
| :--- | :--- | :--- |
| **Runserver** | `python manage.py runserver 8001` | Akses di **http://127.0.0.1:8001/** |

---

## 📌 LOGIKA ARSITEKTUR

| Komponen | Tujuan | Ketergantungan |
| :--- | :--- | :--- |
| **Daphne (T1)** | Menghubungkan *browser* dengan *Channel Layer* (Redis) untuk notifikasi. | Redis |
| **Worker (T2)** | Mengambil tugas dari Redis dan menjalankannya. | Redis |
| **Beat (T3)** | Secara berkala memasukkan tugas terjadwal ke antrian Redis. | Redis & Database |

---

## 🚨 Troubleshooting

Jika notifikasi real-time gagal:

1.  Pastikan **Redis** berjalan.
2.  Pastikan **Daphne (T1)** dan **Worker (T2)** berjalan tanpa *error* koneksi Redis.
3.  Jika tugas Celery macet, **bersihkan antrian** (lakukan saat T2 dan T3 dihentikan):
    ```bash
    celery -A ProyekBarokah purge
    ```