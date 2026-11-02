# Online Book Catalog Organizer (Gramedia Scraper)

### Ujian Tengah Semester (UTS) - Mata Kuliah Automation Systems

**Program Studi Teknik Informatika — Universitas Pelita Bangsa (TA 2025/2026)**  
**Dosen Pengampu:** Anggi Muhammad Rifa'i, M.Kom

---

## 📖 Deskripsi Proyek

Proyek ini adalah sistem otomatisasi berbasis Python (_Command Line Interface_ / CLI) yang berfungsi untuk mengumpulkan, memfilter, membersihkan, dan mengorganisasi katalog buku dari toko buku daring terbesar di Indonesia: **[Gramedia](https://www.gramedia.com/)**.

Aplikasi ini dibangun untuk mengintegrasikan konsep fundamental otomasi dari buku rujukan **_Automate the Boring Stuff with Python_ (Chapter 9 s/d Chapter 13)** ke dalam satu _pipeline_ otomatisasi terpadu.

---

## 🎯 Integrasi Materi Wajib (_Automate the Boring Stuff with Python_)

| Modul / Materi                |    Chapter     | Implementasi dalam Proyek                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :---------------------------- | :------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Regular Expressions**       | **Chapter 9**  | • **Pola 1:** Membersihkan string mata uang Rupiah (misal `"Rp 95.000,00"`) menjadi integer numerik murni (`95000`) dengan `re.sub(r'[^\d]', '', ...)`.<br>• **Pola 2:** Sanitasi string judul buku & penulis dengan membersihkan karakter non-alfanumerik berbahaya dan merapatkan spasi dengan `re.sub()`.<br>• **Pola 3:** Ekstraksi nomor ISBN-13 standar (`r'\b(97[89]\d{10})\b'`) dari aset metadata URL gambar buku.<br>• **Pola 4:** Validasi sintaks format URL detail dan gambar dengan `re.compile(r'^https?://...')`.                  |
| **Reading and Writing Files** | **Chapter 10** | • Menyimpan _payload response_ mentah dari web ke file `data/raw_data.txt` menggunakan `open()` dengan _encoding_ UTF-8.<br>• Menulis dataset buku terstruktur ke format tabel CSV `output/hasil_scraping.csv` menggunakan modul standar `csv.DictWriter`.<br>• Menghasilkan ringkasan eksekusi otomatis analitik ke `output/laporan.txt` (statistik harga rata-rata, harga terendah, harga tertinggi, dan tanggal eksekusi).                                                                                                                      |
| **Organizing Files**          | **Chapter 11** | • Membangun arsitektur direktori proyek secara dinamis (`data/`, `output/`, `backup/`) menggunakan modul `pathlib.Path` dengan metode `mkdir(parents=True, exist_ok=True)`.<br>• Mengarsipkan dan mengompresi seluruh isi folder `output/` secara otomatis menjadi file `backup/backup_data.zip` menggunakan modul `zipfile.ZipFile(..., zipfile.ZIP_DEFLATED)`.                                                                                                                                                                                   |
| **Command Line Programs**     | **Chapter 12** | • Membangun _interface_ CLI menggunakan modul bawaan `argparse`.<br>• Menyediakan argumen: `--url`, `--keyword`, `--limit`, `--output`, dan flag boolean `--backup`.                                                                                                                                                                                                                                                                                                                                                                               |
| **Web Scraping**              | **Chapter 13** | • Menghadapi arsitektur Gramedia sebagai aplikasi modern _Single Page Application_ (Next.js/React).<br>• Menggunakan _reverse-engineering_ terhadap endpoint API katalog Gramedia (`https://api-service.gramedia.com/api/v2/public/search-result-product`) dengan _custom headers_ browser modern (`User-Agent`, `Referer`, `Origin`).<br>• Mengimplementasikan perulangan pagination multi-halaman otomatis hingga memenuhi target _limit_ buku.<br>• Mengintegrasikan library `BeautifulSoup` (bs4) untuk dekode entitas HTML dan sanitasi teks. |

---

## 📂 Struktur Direktori Proyek

```text
UTS_Project_Kelompok_XX/
│
├── main.py                     # Script utama otomatisasi (modular & terstruktur)
├── requirements.txt            # Daftar dependensi eksternal (requests, bs4)
├── README.md                   # Dokumentasi lengkap, instalasi, dan panduan CLI
│
├── data/
│   └── raw_data.txt            # Data mentah respons HTTP JSON dari endpoint Gramedia
│
├── output/
│   ├── hasil_scraping.csv      # Dataset buku terstruktur (delimiter koma ',')
│   └── laporan.txt             # Laporan analitik ringkasan eksekusi otomatis
│
└── backup/
    └── backup_data.zip         # Arsip zip kompresi isi folder output/
```

---

## 🛠️ Instalasi & Prasyarat Lingkungan

Pastikan **Python 3.8+** telah terinstal pada sistem operasi Anda.

### 1. Kloning atau Buka Folder Proyek

```bash
cd "c:/kumpulan projek/scraping gramedia"
```

### 2. (Opsional) Buat & Aktifkan Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalasi Dependensi

```bash
pip install -r requirements.txt
```

---

## 🚀 Panduan Eksekusi CLI (_Command Line Interface_)

Script dijalankan melalui terminal dengan sintaks dasar berikut:

```bash
python main.py [OPSI]
```

### Daftar Opsi & Parameter Tersedia:

| Argumen CLI | Tipe Data |        Nilai Default         | Keterangan                                                       |
| :---------- | :-------: | :--------------------------: | :--------------------------------------------------------------- |
| `--keyword` | `string`  |          `"python"`          | Kata kunci pencarian judul/topik buku di katalog Gramedia        |
| `--limit`   | `integer` |             `30`             | Target batas minimal jumlah record buku yang diambil             |
| `--output`  | `string`  |    `"hasil_scraping.csv"`    | Nama custom file CSV hasil penyimpanan data terstruktur          |
| `--backup`  |  `flag`   |           `False`            | Flag boolean untuk memicu pembuatan file arsip `backup_data.zip` |
| `--url`     | `string`  | `"https://www.gramedia.com"` | URL dasar website katalog Gramedia                               |

---

### Contoh Perintah Eksekusi Terminal:

#### 1. Eksekusi Standar (30 Buku Topik Python + Backup ZIP Otomatis)

```bash
python main.py --keyword python --limit 30 --backup
```

#### 2. Eksekusi Topik Tertentu (Misal: Novel Fiksi, Limit 50 Buku)

```bash
python main.py --keyword "novel" --limit 50 --output "novel_populer.csv" --backup
```

#### 3. Eksekusi Buku Topik Komputer & Teknologi (Tanpa Backup)

```bash
python main.py --keyword "komputer" --limit 35
```

#### 4. Menampilkan Menu Bantuan Argparse

```bash
python main.py --help
```

---

## 📊 Format Output Data

### 1. Dataset CSV (`output/hasil_scraping.csv`)

File CSV disimpan dengan encoding UTF-8-SIG dan pemisah koma (,) untuk kompatibilitas dengan aplikasi spreadsheet.

- `id_produk`: ID unik katalog produk Gramedia
- `judul_buku`: Judul buku yang telah disanitasi
- `penulis`: Nama penulis / pengarang
- `format_kategori`: Format buku (misal: _soft-cover_, _ebook_)
- `harga_asli`: Harga sebelum diskon (angka integer murni)
- `harga_diskon`: Harga setelah diskon (angka integer murni)
- `diskon_persen`: Persentase potongan harga
- `isbn`: Nomor ISBN-13 standar buku
- `url_detail`: Tautan langsung ke laman detail buku di Gramedia
- `url_gambar`: Tautan langsung gambar sampul buku di server CDN

### 2. Laporan Analitik Eksekusi (`output/laporan.txt`)

Berisi ringkasan otomatis setiap kali script dijalankan:

- Tanggal dan jam eksekusi
- Kata kunci pencarian & target URL
- Total record yang berhasil diperoleh
- Statistik harga buku: Rata-rata harga, harga termurah, harga termahal
- Status dan lokasi file arsip backup ZIP

---

## 🛡️ Robust Error Handling & Keandalan Sistem

Aplikasi dilengkapi blok proteksi `try-except` menyeluruh:

1. **Network & Connection Failure:** Menangani `requests.exceptions.Timeout` dan `ConnectionError` jika terjadi gangguan koneksi internet.
2. **Empty Data Handling:** Memberikan pesan peringatan ramah jika kata kunci pencarian tidak menghasilkan buku di server Gramedia.
3. **File System Safety:** Menggunakan `pathlib.Path` dengan penanganan `OSError` dan pembuatan direktori otomatis tanpa konflik.
4. **Data Sanitization:** Mencegah terjadinya error pada karakter non-standar atau tag HTML menggunakan kombinasi `BeautifulSoup` dan `re`.

---

## 👥 Informasi Pengembang

- **Mata Kuliah:** Automation Systems
- **Program Studi:** Teknik Informatika
- **Fakultas:** Teknik
- **Perguruan Tinggi:** Universitas Pelita Bangsa
- **Dosen Pengampu:** Anggi Muhammad Rifa'i, M.Kom
