# Online Book Catalog Organizer (Gramedia Scraper)

## Identitas Kelompok

**Mata Kuliah:** Automation Systems  
**Program Studi:** Teknik Informatika – Universitas Pelita Bangsa  
**Dosen Pengampu:** Anggi Muhammad Rifa'i, M.Kom  
**Kelompok:** Gak Tahu

| No. | Nama Anggota     | NIM       |
| :--: | ---------------- | --------- |
|   1 | Andrian Lusmana  | 312310199 |
|   2 | Aldi Hermansyah  | 312310200 |
|   3 | Dzikry Eza Yusuf | 312310731 |

## Deskripsi Proyek

Online Book Catalog Organizer adalah aplikasi otomatisasi berbasis Python dengan antarmuka Command Line Interface (CLI). Aplikasi ini mengambil data katalog buku dari Gramedia berdasarkan kata kunci, membersihkan data, menyimpan hasil ke CSV dan TXT, serta membuat laporan dan backup ZIP.

## Fitur Utama

- Mengambil data buku Gramedia berdasarkan kata kunci.
- Mengambil data dari beberapa halaman menggunakan pagination.
- Membersihkan harga dan teks serta mengekstrak ISBN dan memvalidasi URL menggunakan Regular Expressions.
- Menyimpan respons JSON mentah ke `data/raw_data.txt`.
- Menyimpan data buku ke file CSV.
- Membuat laporan ringkasan ke `output/laporan.txt`.
- Membuat arsip ZIP dari folder `output/`.
- Menyediakan pilihan pencarian, jumlah data, nama file output, URL dasar, dan backup melalui CLI.

## Integrasi Materi UTS

| Chapter | Materi                    | Penerapan dalam Proyek                                                                                                     |
| ------: | ------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
|       9 | Regular Expressions       | Membersihkan harga dan teks, mengekstrak ISBN-13, serta memvalidasi URL menggunakan modul `re`.                            |
|      10 | Reading and Writing Files | Membaca dan menyimpan data menggunakan `open()` serta menulis CSV menggunakan `csv.DictWriter`.                            |
|      11 | Organizing Files          | Membuat direktori menggunakan `pathlib` dan membuat arsip ZIP menggunakan `zipfile`.                                       |
|      12 | Command Line Programs     | Mengelola argumen CLI menggunakan `argparse`.                                                                              |
|      13 | Web Scraping              | Mengambil data katalog melalui API Gramedia menggunakan `requests`, pagination, dan `BeautifulSoup` untuk pemrosesan teks. |

## Struktur Direktori

```text
Scraping_gramedia-main/
├── main.py
├── requirements.txt
├── README.md
├── data/
│   └── raw_data.txt
├── output/
│   ├── hasil_scraping.csv
│   ├── novel_populer.csv
│   └── laporan.txt
├── backup/
│   └── backup_data.zip
└── dokumentasi/
    └── laporan_uts.pdf  (ditambahkan saat finalisasi laporan)
```

## Instalasi

Pastikan Python 3.8 atau versi lebih baru sudah terpasang.

1. Buka terminal pada folder proyek.
2. Buat dan aktifkan virtual environment (opsional):

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   venv\Scripts\Activate.ps1
   ```

3. Instal dependency:

   ```bash
   pip install -r requirements.txt
   ```

## Panduan Eksekusi CLI

| Argumen     | Fungsi                                                              |
| ----------- | ------------------------------------------------------------------- |
| `--url`     | Menentukan URL dasar website (default: `https://www.gramedia.com`). |
| `--keyword` | Menentukan kata kunci pencarian (default: `python`).                |
| `--limit`   | Menentukan jumlah maksimum data yang akan diambil (default: `30`).  |
| `--output`  | Menentukan nama file CSV (default: `hasil_scraping.csv`).           |
| `--backup`  | Mengaktifkan pembuatan arsip ZIP pada folder `backup/`.             |

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

## Hasil Output

| File                        | Keterangan                                                                             |
| --------------------------- | -------------------------------------------------------------------------------------- |
| `data/raw_data.txt`         | Respons JSON mentah dari API Gramedia.                                                 |
| `output/hasil_scraping.csv` | Dataset hasil pencarian dengan nama file default.                                      |
| `output/novel_populer.csv`  | Contoh dataset hasil pencarian novel menggunakan nama file khusus.                     |
| `output/laporan.txt`        | Ringkasan waktu eksekusi, kata kunci, jumlah data, statistik harga, dan status backup. |
| `backup/backup_data.zip`    | Arsip ZIP yang berisi file-file pada folder `output/`.                                 |

Kolom dataset CSV:

`id_produk`, `judul_buku`, `penulis`, `format_kategori`, `harga_asli`, `harga_diskon`, `diskon_persen`, `isbn`, `url_detail`, dan `url_gambar`.

Nilai pada `format_kategori` mengikuti informasi format atau kategori yang tersedia dari sumber API.

---

Berikut adalah penjelasan mengenai chapter 9-13 yang bisa diakses melalui [Penjelasan_Chapter_9-13.md](Penjelasan_Chapter_9-13.md)
