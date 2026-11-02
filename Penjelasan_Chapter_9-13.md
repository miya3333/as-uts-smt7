# Panduan Penjelasan Kode `main.py` — Chapter 9 sampai 13

**Proyek:** Online Book Catalog Organizer  
**Sumber data:** Katalog Gramedia  
**Mata kuliah:** Automation Systems

Dokumen ini menjelaskan bagian kode `main.py` yang menerapkan materi Chapter 9–13 dari *Automate the Boring Stuff with Python*. Nomor baris mengacu pada file `main.py` yang diperiksa.

## Gambaran alur program

Saat program dijalankan, alurnya secara umum seperti ini:

1. Menampilkan identitas aplikasi melalui `print_banner()`.
2. Membaca argumen terminal melalui `argparse`.
3. Memvalidasi nilai `--limit`.
4. Menyiapkan folder `data`, `output`, dan `backup`.
5. Mengambil data katalog Gramedia melalui API.
6. Membersihkan dan menyusun data buku.
7. Menyimpan data mentah, CSV, dan laporan.
8. Membuat ZIP apabila opsi `--backup` digunakan.
9. Menampilkan ringkasan hasil proses di terminal.

---

## Chapter 9 — Regular Expressions

**Materi:** Menggunakan regular expression atau Regex untuk mencari, mengambil, memvalidasi, dan membersihkan pola teks.

Import Regex berada di **baris 28**:

```python
import re
```

Pada proyek ini, Regex digunakan melalui empat fungsi berikut.

### 1. Membersihkan harga — `clean_price_regex()`

**Lokasi:** baris 123–155  
**Dipanggil:** baris 337–342

```python
price_str = re.sub(r",\d{2}$", "", price_str)
digits_only = re.sub(r"[^\d]", "", price_str)
```

**Penjelasan:**

- `re.sub()` mengganti bagian teks yang cocok dengan pola Regex.
- Pola `,\d{2}$` menghapus dua angka desimal di belakang koma, misalnya `,00`.
- Pola `[^\d]` memilih semua karakter yang bukan angka, lalu menghapusnya.
- Hasil akhirnya dikonversi menjadi `int` agar harga dapat dihitung.

**Contoh:**

```text
Input  : Rp 95.000,00
Proses : menghapus ,00 dan karakter selain angka
Output : 95000
```

Fungsi ini membuat nilai harga lebih mudah diolah untuk menghitung statistik.

### 2. Membersihkan teks — `sanitize_text_regex()`

**Lokasi:** baris 157–185  
**Dipanggil:** baris 332–335

```python
clean_text = re.sub(r"[\r\n\t]+", " ", clean_text)
clean_text = re.sub(r"[^\w\s\-\.\,\:\;\(\)\'\"\/]", "", clean_text)
clean_text = re.sub(r"\s+", " ", clean_text).strip()
```

**Penjelasan:**

- Baris pertama mengganti karakter baris baru, carriage return, dan tab menjadi spasi.
- Baris kedua membuang karakter yang tidak termasuk kelompok karakter yang diizinkan.
- Baris ketiga merapatkan spasi berulang menjadi satu spasi dan menghapus spasi di awal atau akhir.
- Sebelum Regex dijalankan, `BeautifulSoup` digunakan untuk mengambil teks dari kemungkinan markup HTML. Bagian ini juga berkaitan dengan Chapter 13.

**Contoh:**

```text
Input  : "  Belajar\n\tPython   Dasar  "
Output : "Belajar Python Dasar"
```

Fungsi ini dipakai untuk merapikan judul, penulis, dan format buku.

### 3. Mengekstrak ISBN-13 — `extract_isbn_regex()`

**Lokasi:** baris 188–207  
**Dipanggil:** baris 343–344

```python
match = re.search(r"(97[89]\d{10})", text_source)
```

**Penjelasan pola:**

- `97[89]` berarti angka diawali `978` atau `979`.
- `\d{10}` berarti diikuti tepat 10 digit.
- `re.search()` mencari pola tersebut di dalam teks dan mengambil kecocokan pertama.

**Contoh:**

```text
Input  : https://cdn.gramedia.com/items/9786026948007_cover.jpg
Output : 9786026948007
```

Pada kode, ISBN dari field API digunakan lebih dahulu. Jika kosong, program mencoba mengambil ISBN dari URL gambar. Jika tetap tidak ditemukan, nilainya menjadi `-`.

### 4. Memvalidasi URL — `validate_url_regex()`

**Lokasi:** baris 210–230  
**Dipanggil:** baris 346–348

```python
url_pattern = re.compile(
    r"^https?://"
    r"(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"
    r"(?::\d{1,5})?"
    r"(?:/[^\s]*)?$",
    re.IGNORECASE,
)
return bool(url_pattern.match(url.strip()))
```

**Penjelasan:**

- `^https?://` memastikan URL diawali `http://` atau `https://`.
- Bagian domain memeriksa susunan nama host dan ekstensi domain.
- `(?::\d{1,5})?` mengizinkan port opsional.
- Bagian terakhir mengizinkan path URL.
- `re.IGNORECASE` membuat pemeriksaan tidak membedakan huruf besar dan kecil.
- Hasil `True` berarti format URL cocok dengan pola. Ini memeriksa bentuk URL, bukan memastikan halaman benar-benar dapat dibuka.

**Inti Chapter 9:** Regex membantu membersihkan harga dan teks, menemukan ISBN, serta memeriksa bentuk URL sebelum data disimpan.

---

## Chapter 10 — Reading and Writing Files

**Materi:** Membaca dan menulis file menggunakan `open()`, serta mengolah file teks dan CSV.

Import yang berkaitan berada di **baris 29–30**:

```python
import csv
import json
```

### 1. Menyimpan data mentah — `save_raw_data()`

**Lokasi:** baris 375–389  
**Dipanggil:** baris 661–662

```python
with open(destination_path, mode="w", encoding="utf-8") as file:
    file.write(raw_content)
```

**Penjelasan:**

- `open()` membuka atau membuat file tujuan.
- Mode `w` berarti menulis dan mengganti isi file jika file tersebut sudah ada.
- `encoding="utf-8"` digunakan untuk mendukung karakter teks.
- `write()` menuliskan respons mentah API yang sudah diserialisasi menjadi JSON.

Hasilnya disimpan di `data/raw_data.txt`. File ini berguna untuk menyimpan data sumber sebelum atau tanpa melihat bentuk tabel CSV.

### 2. Menyimpan dataset CSV — `save_books_to_csv()`

**Lokasi:** baris 391–434  
**Dipanggil:** baris 664–665

```python
with open(
    destination_path,
    mode="w",
    encoding="utf-8-sig",
    newline=""
) as csv_file:
    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames,
        delimiter="," 
    )
    writer.writeheader()
    writer.writerows(books)
```

**Penjelasan:**

- `fieldnames` menentukan nama dan urutan kolom CSV.
- `csv.DictWriter` menulis setiap data buku dari dictionary ke kolom yang sesuai.
- `delimiter=","` menetapkan koma sebagai pemisah kolom.
- `writeheader()` menulis baris judul kolom.
- `writerows(books)` menulis seluruh record buku.
- `utf-8-sig` membantu aplikasi spreadsheet mengenali encoding UTF-8.
- `newline=""` menghindari penambahan baris kosong yang tidak diinginkan pada CSV.

Kolom yang disimpan adalah ID produk, judul, penulis, format/kategori, harga asli, harga diskon, diskon, ISBN, URL detail, dan URL gambar.

### 3. Membuat laporan eksekusi — `generate_execution_report()`

**Lokasi:** baris 435–517  
**Dipanggil:** baris 672–680 atau 685–694

Bagian perhitungan statistik:

```python
prices = [b["harga_diskon"] for b in books if b["harga_diskon"] > 0]
avg_price = sum(prices) / len(prices) if prices else 0
min_price = min(prices) if prices else 0
max_price = max(prices) if prices else 0
```

**Penjelasan:**

- Program mengambil harga diskon yang lebih besar dari nol.
- `sum()` dan pembagian menghitung rata-rata harga.
- `min()` mencari harga terendah.
- `max()` mencari harga tertinggi.
- Jika tidak ada harga valid, nilainya diisi nol agar perhitungan tidak menyebabkan pembagian dengan nol.

Selanjutnya, program menyusun informasi laporan dalam `report_content`, seperti waktu eksekusi, keyword, jumlah buku, statistik harga, dan status backup. Laporan ditulis ke `output/laporan.txt` menggunakan `open()` dan `write()`.

**Inti Chapter 10:** Program menyimpan tiga jenis keluaran: respons mentah JSON dalam TXT, dataset terstruktur dalam CSV, dan ringkasan statistik dalam TXT.

---

## Chapter 11 — Organizing Files

**Materi:** Mengatur direktori dan file, serta membuat arsip ZIP.

Import yang digunakan berada di **baris 31 dan 33**:

```python
import zipfile
from pathlib import Path
```

### 1. Menentukan direktori dasar dan membuat folder — `setup_directories()`

**Lokasi:** baris 67–91  
**Penentuan direktori dasar:** baris 44  
**Dipanggil:** baris 637–642

```python
directories = {
    "data": base_path / "data",
    "output": base_path / "output",
    "backup": base_path / "backup",
}

for name, dir_path in directories.items():
    dir_path.mkdir(parents=True, exist_ok=True)
```

**Penjelasan:**

- `Path` digunakan untuk membentuk dan mengelola lokasi folder secara lebih praktis.
- `BASE_DIR` pada baris 44 menunjuk ke direktori tempat `main.py` berada.
- Operator `/` pada objek `Path` digunakan untuk menyusun alamat folder.
- `mkdir()` membuat direktori.
- `parents=True` mengizinkan pembuatan direktori induk jika diperlukan.
- `exist_ok=True` mencegah error apabila direktori sudah tersedia.

Program memastikan tiga folder tersedia: `data/`, `output/`, dan `backup/`.

### 2. Membuat arsip ZIP — `create_backup_archive()`

**Lokasi:** baris 94–118  
**Dipanggil:** baris 667–682

```python
with zipfile.ZipFile(zip_dest_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
    for file_path in source_dir.rglob("*"):
        if file_path.is_file():
            arcname = file_path.relative_to(source_dir)
            zip_file.write(file_path, arcname=arcname)
```

**Penjelasan:**

- `ZipFile(..., "w", ZIP_DEFLATED)` membuat arsip ZIP baru dengan kompresi.
- `rglob("*")` menelusuri file dan subfolder di dalam direktori sumber.
- `is_file()` memastikan hanya file yang dimasukkan.
- `relative_to()` membuat nama file di dalam ZIP relatif terhadap folder sumber, sehingga struktur arsip lebih rapi.
- `write()` memasukkan file ke dalam ZIP.

Pada implementasi saat ini, sumber backup adalah folder `output/`. Arsip dibuat di `backup/backup_data.zip`.

**Catatan penting:** `data/raw_data.txt` belum termasuk dalam ZIP karena fungsi backup hanya menerima folder `output/` sebagai sumber.

**Inti Chapter 11:** `pathlib` memastikan struktur folder tersedia secara otomatis, sedangkan `zipfile` mengarsipkan hasil pemrosesan ke dalam ZIP.

---

## Chapter 12 — Command Line Programs

**Materi:** Membuat antarmuka terminal dan menerima parameter dari pengguna menggunakan `argparse`.

Import berada di **baris 32**:

```python
import argparse
```

### 1. Membuat parser CLI — `build_cli_parser()`

**Lokasi:** baris 522–580

```python
parser = argparse.ArgumentParser(
    prog="main.py",
    description="Aplikasi Otomatisasi Scraping & Pengorganisasian Katalog Buku Gramedia",
)
```

Parser menjadi pengatur argumen yang dapat diberikan pengguna ketika menjalankan program.

### 2. Mendefinisikan argumen

**Lokasi:** baris 550–577

| Argumen | Fungsi | Nilai default |
|---|---|---|
| `--url` | Menentukan URL dasar website | `https://www.gramedia.com` |
| `--keyword` | Menentukan kata kunci pencarian | `python` |
| `--limit` | Menentukan batas jumlah buku | `30` |
| `--output` | Menentukan nama file CSV | `hasil_scraping.csv` |
| `--backup` | Mengaktifkan pembuatan ZIP | Tidak aktif |

Contoh penggunaan:

```powershell
python main.py --keyword "novel" --limit 50 --output "novel_populer.csv" --backup
```

Artinya, program mencari buku dengan keyword `novel`, mengambil maksimal 50 record, menyimpan CSV dengan nama `novel_populer.csv`, dan mengaktifkan backup.

### 3. Membaca argumen dan memvalidasi input

**Lokasi:** baris 628–635

```python
parser = build_cli_parser()
args = parser.parse_args()

if args.limit <= 0:
    print("[!] Nilai --limit harus bilangan positif lebih dari 0.", file=sys.stderr)
    sys.exit(1)
```

**Penjelasan:**

- `parse_args()` membaca argumen yang diketik pengguna di terminal.
- Nilainya disimpan dalam objek `args`, kemudian digunakan oleh fungsi utama.
- Program memeriksa agar `--limit` lebih besar dari nol.
- `sys.exit(1)` menghentikan program dengan kode keluar 1 jika nilai tidak valid.

**Inti Chapter 12:** Pengguna dapat mengatur pencarian dan penyimpanan melalui terminal tanpa perlu mengubah kode program.

---

## Chapter 13 — Web Scraping

**Materi:** Mengambil data dari website menggunakan HTTP request, membaca respons, dan mengolah data hasil pengambilan.

Import yang digunakan berada di **baris 37–38**:

```python
import requests
from bs4 import BeautifulSoup
```

### 1. Menentukan endpoint dan HTTP headers

**Lokasi:** baris 44–61

```python
GRAMEDIA_API_ENDPOINT = (
    "https://api-service.gramedia.com/api/v2/public/search-result-product"
)
```

Program mengambil data katalog melalui endpoint API Gramedia. `DEFAULT_HEADERS` berisi informasi seperti `User-Agent`, `Accept`, `Origin`, dan `Referer` yang dikirim bersama request.

### 2. Mengambil data katalog — `scrape_gramedia_catalog()`

**Lokasi:** baris 236–369

Membuat session dan mengirim request:

```python
session = requests.Session()
session.headers.update(DEFAULT_HEADERS)

response = session.get(api_endpoint, params=params, timeout=15)
response.raise_for_status()
payload = response.json()
```

**Penjelasan:**

- `requests.Session()` membuat sesi HTTP agar konfigurasi dapat digunakan kembali.
- `headers.update()` memasang header default.
- `session.get()` mengirim HTTP GET ke endpoint dengan parameter pencarian.
- `timeout=15` memberi batas waktu request 15 detik.
- `raise_for_status()` memunculkan error jika respons HTTP menunjukkan kegagalan.
- `response.json()` membaca respons API sebagai data Python.

### 3. Mengatur pagination

**Lokasi:** baris 268–280 dan 305–367

```python
page = 1
per_page = 20

while len(scraped_books) < limit and page <= total_pages_available:
    params = {
        "keyword": keyword,
        "per_page": per_page,
        "page": page,
    }
```

**Penjelasan:**

- `page` menentukan halaman yang sedang diminta.
- `per_page` menentukan jumlah produk yang diminta per halaman.
- `while` terus berjalan selama jumlah data belum mencapai `limit` dan halaman masih tersedia.
- `total_page` dibaca dari metadata respons API.
- Setelah produk pada halaman diproses, `page += 1` berpindah ke halaman berikutnya.

Dengan pagination, program dapat mengambil data dari beberapa halaman, bukan hanya halaman pertama.

### 4. Menangani kesalahan request dan data kosong

**Lokasi:** baris 289–310

Program menangani beberapa kondisi:

- `Timeout`: server tidak merespons dalam batas waktu.
- `ConnectionError`: terjadi masalah koneksi.
- `RequestException`: terjadi kesalahan request HTTP lainnya.
- `JSONDecodeError`: respons tidak dapat dibaca sebagai JSON.
- Data kosong: program menghentikan pagination ketika daftar produk tidak tersedia.

Di fungsi `main()`, baris 655–659, program juga memeriksa apakah hasil scraping kosong dan memberikan pesan kepada pengguna.

### 5. Mengolah data produk

**Lokasi:** baris 314–363

Setelah respons diterima, program mengambil informasi produk seperti:

- ID produk.
- Judul buku.
- Penulis.
- Format.
- Harga asli dan harga diskon.
- Persentase diskon.
- ISBN.
- URL detail dan URL gambar.

Data tersebut kemudian dibersihkan melalui fungsi Regex pada Chapter 9 dan disusun ke dalam `book_record` berbentuk dictionary.

### 6. Peran BeautifulSoup

**Lokasi:** baris 172–174 di `sanitize_text_regex()`

```python
soup = BeautifulSoup(str(raw_text), "html.parser")
clean_text = soup.get_text(separator=" ").strip()
```

BeautifulSoup membantu mengambil teks bersih dari string yang mungkin masih mengandung markup HTML. Setelah itu, Regex merapikan karakter dan spasi.

**Inti Chapter 13:** Program mengambil katalog Gramedia melalui endpoint API menggunakan Requests, membaca respons JSON, melakukan pagination, menangani kesalahan request, dan membersihkan teks dengan bantuan BeautifulSoup.

---

## Ringkasan lokasi kode per chapter

| Chapter | Materi | Fungsi atau bagian utama | Baris kode |
|---|---|---|---:|
| 9 | Regular Expressions | `clean_price_regex()` | 123–155 |
| 9 | Regular Expressions | `sanitize_text_regex()` | 157–185 |
| 9 | Regular Expressions | `extract_isbn_regex()` | 188–207 |
| 9 | Regular Expressions | `validate_url_regex()` | 210–230 |
| 10 | Reading and Writing Files | `save_raw_data()` | 375–389 |
| 10 | Reading and Writing Files | `save_books_to_csv()` | 391–434 |
| 10 | Reading and Writing Files | `generate_execution_report()` | 435–517 |
| 11 | Organizing Files | `setup_directories()` | 67–91 |
| 11 | Organizing Files | `create_backup_archive()` | 94–118 |
| 12 | Command Line Programs | `build_cli_parser()` | 522–580 |
| 12 | Command Line Programs | Parsing dan validasi argumen | 628–635 |
| 13 | Web Scraping | Konfigurasi endpoint dan headers | 44–61 |
| 13 | Web Scraping | `scrape_gramedia_catalog()` | 236–369 |
| 13 | Web Scraping | Penggunaan BeautifulSoup | 172–174 |

## Penjelasan singkat

**Chapter 9:** Menggunakan Regex untuk membersihkan harga, merapikan teks, mengambil ISBN-13 dari URL gambar, dan memvalidasi format URL. Tujuannya agar data yang masuk ke CSV lebih terstruktur.

**Chapter 10:** Menyimpan respons API mentah ke TXT, data buku yang sudah dibersihkan ke CSV, dan ringkasan statistik ke laporan TXT. Proses penulisan menggunakan `open()` dan `csv.DictWriter`.

**Chapter 11:** Menggunakan `pathlib` untuk membuat folder data, output, dan backup secara otomatis. Kemudian, `zipfile` digunakan untuk mengompresi isi folder output menjadi arsip ZIP.

**Chapter 12:** Menggunakan `argparse` agar pengguna dapat mengatur URL, keyword, jumlah data, nama output, dan opsi backup langsung dari terminal.

**Chapter 13:** Menggunakan Requests untuk mengambil data katalog dari API Gramedia. Data JSON diproses dengan pagination, kemudian teks dibersihkan menggunakan BeautifulSoup dan Regex sebelum disimpan.

## Catatan

1. Program mengambil data dari endpoint API katalog Gramedia, bukan mengotomatisasi klik pada browser.
2. BeautifulSoup digunakan untuk membersihkan kemungkinan markup HTML pada teks, sedangkan pengambilan katalog dilakukan melalui Requests dan API JSON.
3. Fungsi backup saat ini mengarsipkan folder `output/`, bukan folder `data/`.
4. `validate_url_regex()` memeriksa pola atau format URL, bukan memastikan URL dapat diakses.
5. Nilai `format_kategori` berasal dari field `format` jika tersedia; field `category_slugs` digunakan sebagai alternatif. Jika API tidak menyediakan kategori, hasilnya tidak otomatis menjadi kategori genre buku.
6. Pada alur saat ini, laporan ditulis dengan status backup berhasil sebelum fungsi pembuatan ZIP dipanggil. Jadi, apabila pembuatan ZIP gagal, isi laporan berpotensi tidak mencerminkan hasil backup yang sebenarnya. Ini merupakan bagian yang dapat diperbaiki pada kode.
