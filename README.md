# 🏪 Aplikasi Pengelolaan Stok Kantin Sekolah

> **Aplikasi berbasis Python + Streamlit untuk mengelola stok kantin sekolah dengan fitur barcode scanning**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

---

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Teknologi](#-teknologi)
- [Instalasi](#-instalasi)
- [Cara Penggunaan](#-cara-penggunaan)
- [Struktur Folder](#-struktur-folder)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

---

## 🌟 Fitur Utama

### 1️⃣ **Dashboard Real-time**
- Statistik produk dan stok
- Grafik penjualan harian
- Alert stok menipis
- Ringkasan keuntungan

### 2️⃣ **Data Master Produk (CRUD)**
- Tambah, Edit, Hapus produk
- Kategori produk
- Manajemen stok
- Harga modal & jual

### 3️⃣ **Barcode System**
- **Generate barcode otomatis** (Code128)
- **Scan via webcam** (pyzxing - Windows compatible!)
- **Input manual** (alternatif)
- **Batch generate** untuk banyak produk

### 4️⃣ **Transaksi Penjualan**
- Scan barcode untuk transaksi cepat
- Pencatatan otomatis
- Pengurangan stok real-time
- Perhitungan keuntungan

### 5️⃣ **Laporan & Analisis**
- Laporan penjualan harian
- Grafik keuntungan
- Produk terlaris
- Export ke Excel

### 6️⃣ **Backup & Export**
- Backup otomatis
- Export data ke Excel/CSV
- Restore data
- Clean old backups

---

## 🛠️ Teknologi

### Core
- **Python 3.8+** - Programming language
- **Streamlit 1.31** - Web framework
- **Pandas 2.1** - Data processing
- **Plotly 5.18** - Interactive charts

### Barcode
- **python-barcode 0.15** - Generate barcode
- **OpenCV 4.9** - Image processing
- **pyzxing 0.2** - Barcode scanner (Windows compatible!)

### Storage
- **CSV files** - Database
- **100% Offline** - No internet needed

---

## 📥 Instalasi

### Prerequisites
- Python 3.8 atau lebih baru
- Webcam (optional, untuk scan barcode)
- Windows/Linux/MacOS

### Langkah Instalasi

#### **Windows**

1. **Clone atau download repository**
   ```bash
   git clone <repository-url>
   cd kantin-sekolah
   ```

2. **Jalankan installer**
   ```bash
   install_windows.bat
   ```
   
   Installer akan:
   - ✅ Membuat virtual environment
   - ✅ Install semua dependencies
   - ✅ Setup folders
   - ✅ Test installation

3. **Jalankan aplikasi**
   ```bash
   run.bat
   ```
   
   Atau manual:
   ```bash
   myenv\Scripts\activate
   streamlit run app.py
   ```

#### **Linux/Mac**

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd kantin-sekolah
   ```

2. **Buat virtual environment**
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Cara Penggunaan

### 1. Login
- **Username**: `admin`
- **Password**: `admin123`

### 2. Tambah Produk
1. Pilih menu **"📦 Data Master"**
2. Tab **"➕ Tambah"**
3. Isi form:
   - Barcode ID (contoh: BRK001)
   - Nama produk
   - Kategori
   - Stok
   - Harga modal & jual
4. Klik **"💾 Simpan Produk"**
5. Barcode otomatis di-generate!

### 3. Generate Barcode Batch
1. Menu **"📦 Data Master"** → Tab **"🏷️ Generate Barcode"**
2. Pilih mode:
   - **Semua Produk**: Generate ulang semua
   - **Hanya yang Belum Ada**: Generate yang missing saja
3. Klik **"🏷️ GENERATE BARCODE"**
4. Download atau print barcode dari folder `barcodes/`

### 4. Scan Barcode & Transaksi

#### **Opsi 1: Webcam Scanner** (Recommended)
1. Menu **"📷 Scan Barcode"** → Tab **"📷 Webcam Scanner"**
2. Klik **"📷 Mulai Scan Barcode"**
3. Arahkan barcode ke webcam
4. Barcode terdeteksi otomatis
5. Masukkan jumlah
6. Klik **"💸 PROSES PENJUALAN"**

#### **Opsi 2: Input Manual** (Alternative)
1. Menu **"📷 Scan Barcode"** → Tab **"⌨️ Input Manual"**
2. Ketik Barcode ID (contoh: BRK001)
3. Klik **"🔍 Cari Produk"**
4. Masukkan jumlah
5. Klik **"💸 PROSES PENJUALAN"**

### 5. Lihat Laporan
1. Menu **"📊 Laporan"**
2. Pilih range tanggal
3. Lihat grafik:
   - Penjualan harian
   - Keuntungan
   - Produk terlaris
4. Export ke Excel jika perlu

---

## 📁 Struktur Folder

```
kantin-sekolah/
├── app.py                      # Main application
├── requirements.txt            # Dependencies
├── install_windows.bat         # Installer (Windows)
├── run.bat                     # Runner (Windows)
│
├── modules/                    # Custom modules
│   ├── __init__.py
│   ├── data_handler.py         # CRUD operations
│   ├── barcode_handler.py      # Barcode gen & scan (pyzxing)
│   ├── chart_handler.py        # Charts & statistics
│   └── utils.py                # Utilities
│
├── data/                       # Data storage
│   ├── products.csv            # Products database
│   ├── transactions.csv        # Transactions log
│   ├── backup/                 # Backup files
│   └── exports/                # Exported files
│
├── barcodes/                   # Generated barcodes
│   ├── BRK001.png
│   ├── BRK002.png
│   └── ...
│
└── .streamlit/                 # Streamlit config
    └── config.toml
```

---

## 🔧 Troubleshooting

### ❌ Problem: Webcam scanner tidak berfungsi

**Solusi 1: Gunakan Input Manual**
- Lebih cepat dan sama efektifnya
- Tidak perlu webcam
- 100% reliable

**Solusi 2: Reinstall pyzxing**
```bash
pip uninstall pyzxing opencv-python -y
pip install opencv-python==4.9.0.80
pip install pyzxing==0.2
```

**Solusi 3: Check webcam**
- Pastikan webcam terhubung
- Tutup aplikasi lain yang pakai webcam
- Restart aplikasi

### ❌ Problem: Error saat generate barcode

**Penyebab**: Library python-barcode belum terinstall

**Solusi**:
```bash
pip install python-barcode==0.15.1 Pillow==10.2.0
```

### ❌ Problem: CSV file corrupt

**Solusi**: Restore dari backup
1. Menu **"⚙️ Pengaturan"** → Tab **"💾 Backup"**
2. Lihat list backup
3. Copy file backup ke folder `data/`
4. Rename sesuai kebutuhan

### ❌ Problem: Port 8501 sudah digunakan

**Solusi**:
```bash
streamlit run app.py --server.port 8502
```

---

## ❓ FAQ

### Q: Apakah harus online?
**A**: Tidak! Aplikasi 100% offline. Data disimpan di CSV lokal.

### Q: Apakah bisa di HP/Tablet?
**A**: Bisa! Jalankan di laptop, akses dari HP via network:
```bash
streamlit run app.py --server.address 0.0.0.0
```
Akses dari HP: `http://<IP-laptop>:8501`

### Q: Format barcode apa yang didukung?
**A**: 
- **Generate**: Code128
- **Scan**: Code128, QR Code, EAN, UPC, dan banyak lagi (pyzxing support 20+ format)

### Q: Apakah data aman?
**A**: Ya! Data disimpan lokal di komputer Anda. Buat backup rutin untuk keamanan ekstra.

### Q: Bisa custom login?
**A**: Ya! Edit file `app.py` di fungsi `login_page()`. Ganti username/password sesuai kebutuhan.

### Q: Webcam tidak terdeteksi di Windows?
**A**: Gunakan **Input Manual** sebagai alternatif. Sama cepatnya! Atau pastikan:
- Webcam driver terinstall
- Permission kamera tidak diblok
- Pyzxing terinstall dengan benar

### Q: Bisa multi-user?
**A**: Saat ini single user. Untuk multi-user, perlu upgrade ke database (SQLite/MySQL) dan add user management.

### Q: Export data ke format lain?
**A**: Bisa! Aplikasi support export ke Excel dan CSV. Dari Excel bisa convert ke format lain.

---

## 📊 Keunggulan Pyzxing vs Pyzbar

| Feature | Pyzxing ✅ | Pyzbar ❌ |
|---------|-----------|----------|
| Windows Support | Native | Butuh ZBar DLL |
| Installation | `pip install` saja | Kompleks (DLL eksternal) |
| Format Support | 20+ format | Terbatas |
| Stability | Tinggi | Sering crash di Windows |
| Performance | Good | Better (tapi ribet setup) |

**Kesimpulan**: Pyzxing lebih cocok untuk aplikasi Windows karena instalasi mudah dan stabil!

---

## 🎯 Roadmap

### v1.1 (Coming Soon)
- [ ] Multiple user accounts
- [ ] SQLite database option
- [ ] Print receipt
- [ ] Dashboard widgets customization

### v1.2 (Future)
- [ ] Mobile app (React Native)
- [ ] Cloud backup
- [ ] Multi-store support
- [ ] Advanced analytics

---

## 👥 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat branch baru
3. Commit changes
4. Push ke branch
5. Create Pull Request

---

## 📝 License

MIT License - Bebas digunakan untuk keperluan komersial maupun non-komersial.

---

## 💬 Support

Butuh bantuan? Ada pertanyaan?

- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: your-email@example.com
- **Docs**: Baca README ini lengkap

---

## 🙏 Credits

**Dikembangkan untuk:**
- Tugas Pemrograman Terstruktur
- Solusi digitalisasi kantin sekolah

**Teknologi:**
- Python, Streamlit, Pandas, Plotly
- OpenCV, pyzxing untuk barcode
- 100% paradigma pemrograman terstruktur

---

## ⭐ Give a Star!

Jika aplikasi ini bermanfaat, berikan ⭐ di GitHub!

---

*© 2024 Kantin Sekolah Manager - All Rights Reserved*